from collections import Counter, defaultdict
from math import floor


SCENARIO_RATIO_KEYS = {
    "NORMAL": "normal_ratio",
    "CAPACITY_OVER": "capacity_over_ratio",
    "DUPLICATE": "duplicate_ratio",
    "PREREQUISITE_FAIL": "prerequisite_fail_ratio",
    "TIME_CONFLICT": "time_conflict_ratio",
    "CREDIT_LIMIT": "credit_limit_ratio",
}


def allocate_scenario_counts(payload_config):
    total = payload_config["total_requests"]
    raw = {name: total * payload_config.get(key, 0) for name, key in SCENARIO_RATIO_KEYS.items()}
    counts = {name: floor(value) for name, value in raw.items()}
    remaining = total - sum(counts.values())
    order = sorted(raw, key=lambda name: raw[name] - counts[name], reverse=True)
    for name in order[:remaining]:
        counts[name] += 1
    return counts


class PayloadGenerator:
    table = "enrollment_payload"

    def generate(self, context):
        builder = StatefulPayloadBuilder(context)
        context.data[self.table] = builder.build()


class StatefulPayloadBuilder:
    def __init__(self, context):
        self.context = context
        self.scenario = context.scenario
        self.payload_config = self.scenario["payload"]
        self.counts = allocate_scenario_counts(self.payload_config)
        if sum(self.payload_config.get(key, 0) for key in SCENARIO_RATIO_KEYS.values()) != 1:
            raise ValueError("payload scenario ratios must sum to 1.0")

        self.expected_status = self.payload_config["expected_status"]
        self.total = self.payload_config["total_requests"]
        self.hotspot_ids = sorted(context.metadata["hotspot_course_ids"])
        self.normal_ids = [row["id"] for row in context.data["course"] if row["id"] not in context.metadata["hotspot_course_ids"]]
        self.courses = {row["id"]: row for row in context.data["course"]}
        self.course_times = {row["course_id"]: row for row in context.data["course_time"]}
        self.completed = context.metadata["completed_by_student"]
        self.department_by_student = {row["student_id"]: row["department_id"] for row in context.data["student"]}
        self.prerequisites = defaultdict(list)
        self.prerequisite_course_ids = set()
        for row in context.data["prerequisite"]:
            self.prerequisites[(row["course_id"], row["department_id"])].append(row["pre_course_id"])
            self.prerequisite_course_ids.add(row["course_id"])

        all_students = [row["student_id"] for row in context.data["student"]]
        active_count = self.scenario["traffic"]["active_users"]
        if active_count > len(all_students):
            raise ValueError("traffic.active_users cannot exceed scale.students")
        self.active_students = context.random.sample(all_students, active_count)
        context.metadata["active_student_ids"] = set(self.active_students)

        self.student_enrolled_courses = defaultdict(set)
        self.student_enrolled_timeslots = defaultdict(list)
        self.course_success_count = Counter()
        self.used_student_course_pairs = set()
        self.success_pairs = []
        self.rows = []

        self.safe_hotspot_ids = [course_id for course_id in self.hotspot_ids if course_id not in self.prerequisite_course_ids]
        self.prerequisite_hotspot_ids = [course_id for course_id in self.hotspot_ids if course_id in self.prerequisite_course_ids]
        self.safe_normal_ids = [course_id for course_id in self.normal_ids if course_id not in self.prerequisite_course_ids]

    def build(self):
        self._assert_label_contract()
        offsets = self._scheduled_offsets()

        failure_count = (
            self.counts["CAPACITY_OVER"]
            + self.counts["DUPLICATE"]
            + self.counts["PREREQUISITE_FAIL"]
            + self.counts["TIME_CONFLICT"]
        )
        target_hotspot_requests = round(self.total * self.scenario["traffic"]["hotspot_request_ratio"])
        hotspot_success_count = target_hotspot_requests - failure_count
        normal_success_count = self.counts["NORMAL"] - hotspot_success_count

        if hotspot_success_count < 0 or normal_success_count < 0:
            raise ValueError("scenario ratios require more hotspot failures than total hotspot target")

        self._build_successes(hotspot_success_count, normal_success_count)
        self._build_capacity_over(self.counts["CAPACITY_OVER"])
        self._build_duplicate(self.counts["DUPLICATE"])
        self._build_time_conflict(self.counts["TIME_CONFLICT"])
        self._build_prerequisite_fail(self.counts["PREREQUISITE_FAIL"])

        if len(self.rows) != self.total:
            raise RuntimeError(f"payload size mismatch: actual={len(self.rows)}, expected={self.total}")

        for row, offset in zip(self.rows, offsets):
            row["scheduled_offset_ms"] = offset

        return self.rows

    def _build_successes(self, hotspot_success_count, normal_success_count):
        self._build_success_pool(
            target_count=hotspot_success_count,
            course_pool=self.safe_hotspot_ids,
            fill_subset=True,
        )
        self._build_success_pool(
            target_count=normal_success_count,
            course_pool=self.safe_normal_ids,
            fill_subset=False,
        )

    def _build_success_pool(self, target_count, course_pool, fill_subset):
        if target_count <= 0:
            return
        if not course_pool:
            raise RuntimeError("no course pool available for NORMAL success payloads")

        if fill_subset:
            selected_courses = []
            remaining = target_count
            for course_id in course_pool:
                selected_courses.append(course_id)
                remaining -= self.courses[course_id]["capacity"]
                if remaining <= 0:
                    break
            target_by_course = Counter()
            remaining = target_count
            for course_id in selected_courses:
                amount = min(self.courses[course_id]["capacity"], remaining)
                target_by_course[course_id] = amount
                remaining -= amount
                if remaining == 0:
                    break
        else:
            selected_courses = list(course_pool)
            if not selected_courses:
                raise RuntimeError("no selected courses available for distributed NORMAL successes")
            target_by_course = Counter()
            for index in range(target_count):
                course_id = selected_courses[index % len(selected_courses)]
                if target_by_course[course_id] >= self.courses[course_id]["capacity"]:
                    raise RuntimeError(f"distributed NORMAL target exceeded course capacity for course_id={course_id}")
                target_by_course[course_id] += 1
            remaining = 0

        if remaining:
            raise RuntimeError(f"not enough course capacity for NORMAL successes: missing={remaining}")

        student_index = 0
        for course_id, amount in target_by_course.items():
            for _ in range(amount):
                student_id, student_index = self._find_success_student(course_id, student_index)
                self._append_success(student_id, course_id)

    def _find_success_student(self, course_id, start_index):
        total_students = len(self.active_students)
        for offset in range(total_students):
            index = (start_index + offset) % total_students
            student_id = self.active_students[index]
            if self._can_success(student_id, course_id):
                return student_id, (index + 1) % total_students
        # A full scan should almost always succeed. If it does not, sample the
        # active set randomly a few times before failing with a concrete course.
        for _ in range(1000):
            student_id = self.context.random.choice(self.active_students)
            if self._can_success(student_id, course_id):
                return student_id, start_index
        raise RuntimeError(f"cannot find success candidate for course_id={course_id}")

    def _can_success(self, student_id, course_id):
        if (student_id, course_id) in self.used_student_course_pairs:
            return False
        if course_id in self.completed[student_id]:
            return False
        if self.course_success_count[course_id] >= self.courses[course_id]["capacity"]:
            return False
        if not self._prerequisites_satisfied(student_id, course_id):
            return False
        if self._has_time_conflict(student_id, course_id):
            return False
        return True

    def _append_success(self, student_id, course_id):
        self.used_student_course_pairs.add((student_id, course_id))
        self.student_enrolled_courses[student_id].add(course_id)
        self.student_enrolled_timeslots[student_id].append(self.course_times[course_id])
        self.course_success_count[course_id] += 1
        self.success_pairs.append((student_id, course_id))
        self._append_row(student_id, course_id, "NORMAL")

    def _build_capacity_over(self, count):
        full_courses = [course_id for course_id in self.hotspot_ids if self.course_success_count[course_id] >= self.courses[course_id]["capacity"]]
        if not full_courses and count:
            raise RuntimeError("CAPACITY_OVER requires at least one full hotspot course")
        for index in range(count):
            course_id = full_courses[index % len(full_courses)]
            student_id = self._find_unused_student_for_course(course_id)
            self._append_row(student_id, course_id, "CAPACITY_OVER")

    def _build_duplicate(self, count):
        hotspot_pairs = [(student_id, course_id) for student_id, course_id in self.success_pairs if course_id in self.hotspot_ids]
        if not hotspot_pairs and count:
            raise RuntimeError("DUPLICATE requires a prior successful hotspot pair")
        for index in range(count):
            student_id, course_id = hotspot_pairs[index % len(hotspot_pairs)]
            self._append_row(student_id, course_id, "DUPLICATE")

    def _build_time_conflict(self, count):
        for _ in range(count):
            candidate = self._find_time_conflict_candidate()
            if not candidate:
                raise RuntimeError("TIME_CONFLICT requires an unused overlapping course for a student with prior success")
            student_id, course_id = candidate
            self._append_row(student_id, course_id, "TIME_CONFLICT")

    def _find_time_conflict_candidate(self):
        candidate_courses = [
            course_id for course_id in self.safe_hotspot_ids
            if self.course_success_count[course_id] < self.courses[course_id]["capacity"]
        ]
        self.context.random.shuffle(candidate_courses)
        students = list(self.active_students)
        self.context.random.shuffle(students)
        for student_id in students:
            if not self.student_enrolled_timeslots[student_id]:
                continue
            for course_id in candidate_courses:
                if (student_id, course_id) in self.used_student_course_pairs:
                    continue
                if course_id in self.completed[student_id]:
                    continue
                if self._has_time_conflict(student_id, course_id):
                    return student_id, course_id
        return None

    def _build_prerequisite_fail(self, count):
        candidates_by_course = {}
        for course_id in self.prerequisite_hotspot_ids:
            candidates = []
            if self.course_success_count[course_id] >= self.courses[course_id]["capacity"]:
                continue
            for student_id in self.active_students:
                if (student_id, course_id) in self.used_student_course_pairs:
                    continue
                if course_id in self.completed[student_id]:
                    continue
                required = self.prerequisites.get((course_id, self.department_by_student[student_id]), [])
                if required and any(course not in self.completed[student_id] for course in required):
                    candidates.append((student_id, course_id))
                    if len(candidates) >= 200:
                        break
            if candidates:
                candidates_by_course[course_id] = candidates
        if not candidates_by_course and count:
            raise RuntimeError("PREREQUISITE_FAIL requires missing-prerequisite candidates")
        course_ids = sorted(candidates_by_course)
        per_course_index = Counter()
        for index in range(count):
            course_id = course_ids[index % len(course_ids)]
            candidates = candidates_by_course[course_id]
            student_id, course_id = candidates[per_course_index[course_id] % len(candidates)]
            per_course_index[course_id] += 1
            self._append_row(student_id, course_id, "PREREQUISITE_FAIL")

    def _find_unused_student_for_course(self, course_id):
        start = self.context.random.randint(0, len(self.active_students) - 1)
        for offset in range(len(self.active_students)):
            student_id = self.active_students[(start + offset) % len(self.active_students)]
            if (student_id, course_id) not in self.used_student_course_pairs:
                return student_id
        raise RuntimeError(f"cannot find unused student for course_id={course_id}")

    def _append_row(self, student_id, course_id, scenario_type):
        self.rows.append({
            "student_id": student_id,
            "course_id": course_id,
            "scenario_type": scenario_type,
            "expected_status": self.expected_status[scenario_type],
            "scheduled_offset_ms": 0,
        })

    def _prerequisites_satisfied(self, student_id, course_id):
        required = self.prerequisites.get((course_id, self.department_by_student[student_id]), [])
        return all(course_id in self.completed[student_id] for course_id in required)

    def _has_time_conflict(self, student_id, course_id):
        selected = self.course_times[course_id]
        return any(self._overlaps(selected, timeslot) for timeslot in self.student_enrolled_timeslots[student_id])

    @staticmethod
    def _overlaps(left, right):
        return (
            left["day_of_week"] == right["day_of_week"]
            and left["start_time"] < right["end_time"]
            and right["start_time"] < left["end_time"]
        )

    def _scheduled_offsets(self):
        burst_count = round(self.total * self.scenario["traffic"]["burst_window_ratio"])
        offsets = [self.context.random.randint(0, 9999) for _ in range(burst_count)]
        offsets += [self.context.random.randint(10000, 30000) for _ in range(self.total - burst_count)]
        return sorted(offsets)

    def _assert_label_contract(self):
        for scenario_type, status in self.expected_status.items():
            status = str(status)
            if scenario_type in {"NORMAL", "HOTSPOT"} and status != "200":
                raise ValueError(f"{scenario_type} must use expected_status=200")
            if scenario_type in {"PREREQUISITE_FAIL", "TIME_CONFLICT", "CAPACITY_OVER", "DUPLICATE"} and not status.startswith("4"):
                raise ValueError(f"{scenario_type} must use expected_status=4xx")
