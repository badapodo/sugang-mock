from collections import Counter, defaultdict
from math import ceil, floor

from .base import AUDIT_NULLS


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

        self.student_enrolled_courses = defaultdict(set)
        self.student_enrolled_timeslots = defaultdict(list)
        self.course_success_count = Counter()
        self.used_student_course_pairs = set()
        self.seed_enrollment_pairs = set()
        self.success_pairs = []
        self.rows = []

        self.safe_hotspot_ids = [course_id for course_id in self.hotspot_ids if course_id not in self.prerequisite_course_ids]
        self.prerequisite_hotspot_ids = [course_id for course_id in self.hotspot_ids if course_id in self.prerequisite_course_ids]
        self.safe_normal_ids = [course_id for course_id in self.normal_ids if course_id not in self.prerequisite_course_ids]
        self._allocate_scenario_pools()
        self._prepare_seed_state()

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
        self._build_capacity_over()
        self._build_duplicate()
        self._build_time_conflict()
        self._build_prerequisite_fail()

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
            scenario_type="HOTSPOT",
        )
        self._build_success_pool(
            target_count=normal_success_count,
            course_pool=self.safe_normal_ids,
            fill_subset=False,
            scenario_type="NORMAL",
        )

    def _build_success_pool(self, target_count, course_pool, fill_subset, scenario_type):
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
                self._append_success(student_id, course_id, scenario_type)

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

    def _append_success(self, student_id, course_id, scenario_type):
        self.used_student_course_pairs.add((student_id, course_id))
        self.student_enrolled_courses[student_id].add(course_id)
        self.student_enrolled_timeslots[student_id].append(self.course_times[course_id])
        self.course_success_count[course_id] += 1
        self.success_pairs.append((student_id, course_id))
        self._append_row(student_id, course_id, scenario_type)

    def _build_capacity_over(self):
        for student_id, course_id in self.capacity_plan:
            self._append_row(student_id, course_id, "CAPACITY_OVER")

    def _build_duplicate(self):
        for student_id, course_id in self.duplicate_plan:
            self._append_row(student_id, course_id, "DUPLICATE")

    def _build_time_conflict(self):
        for student_id, course_id in self.time_conflict_plan:
            self._append_row(student_id, course_id, "TIME_CONFLICT")

    def _build_prerequisite_fail(self):
        for student_id, course_id in self.prerequisite_plan:
            self._append_row(student_id, course_id, "PREREQUISITE_FAIL")

    def _allocate_scenario_pools(self):
        all_students = [row["student_id"] for row in self.context.data["student"]]
        prerequisite_candidates = []
        prerequisite_course_by_student = {}
        for student_id in all_students:
            department_id = self.department_by_student[student_id]
            candidates = [
                course_id
                for course_id in self.prerequisite_hotspot_ids
                if course_id not in self.completed[student_id]
                and any(
                    required not in self.completed[student_id]
                    for required in self.prerequisites.get((course_id, department_id), [])
                )
            ]
            if candidates:
                prerequisite_candidates.append(student_id)
                prerequisite_course_by_student[student_id] = candidates

        prerequisite_count = self.counts["PREREQUISITE_FAIL"]
        if len(prerequisite_candidates) < prerequisite_count:
            raise RuntimeError(
                f"not enough independent PREREQUISITE_FAIL students: "
                f"actual={len(prerequisite_candidates)}, required={prerequisite_count}"
            )
        self.context.random.shuffle(prerequisite_candidates)
        self.prerequisite_students = prerequisite_candidates[:prerequisite_count]
        self.prerequisite_plan = [
            (student_id, self.context.random.choice(prerequisite_course_by_student[student_id]))
            for student_id in self.prerequisite_students
        ]

        reserved_students = set(self.prerequisite_students)
        remaining_students = [student_id for student_id in all_students if student_id not in reserved_students]
        self.context.random.shuffle(remaining_students)
        success_count = self.scenario["traffic"]["active_users"] - sum(
            self.counts[name]
            for name in ("CAPACITY_OVER", "DUPLICATE", "PREREQUISITE_FAIL", "TIME_CONFLICT")
        )
        required_students = (
            success_count
            + self.counts["DUPLICATE"]
            + self.counts["TIME_CONFLICT"]
            + self.counts["CAPACITY_OVER"]
        )
        if success_count <= 0 or len(remaining_students) < required_students:
            raise RuntimeError("traffic.active_users does not leave enough disjoint scenario students")

        cursor = 0
        self.active_students = remaining_students[cursor:cursor + success_count]
        cursor += success_count
        self.duplicate_students = remaining_students[cursor:cursor + self.counts["DUPLICATE"]]
        cursor += self.counts["DUPLICATE"]
        self.time_conflict_students = remaining_students[cursor:cursor + self.counts["TIME_CONFLICT"]]
        cursor += self.counts["TIME_CONFLICT"]
        self.capacity_students = remaining_students[cursor:cursor + self.counts["CAPACITY_OVER"]]
        cursor += self.counts["CAPACITY_OVER"]
        self.seed_filler_students = remaining_students[cursor:]

        payload_students = (
            set(self.active_students)
            | set(self.duplicate_students)
            | set(self.time_conflict_students)
            | set(self.capacity_students)
            | set(self.prerequisite_students)
        )
        if len(payload_students) != self.scenario["traffic"]["active_users"]:
            raise RuntimeError("scenario student pools overlap or do not match traffic.active_users")
        self.context.metadata["active_student_ids"] = payload_students
        self.context.metadata["scenario_student_ids"] = {
            "SUCCESS": set(self.active_students),
            "DUPLICATE": set(self.duplicate_students),
            "TIME_CONFLICT": set(self.time_conflict_students),
            "CAPACITY_OVER": set(self.capacity_students),
            "PREREQUISITE_FAIL": set(self.prerequisite_students),
        }

    def _prepare_seed_state(self):
        available_hotspot = [
            course_id
            for course_id in self.safe_hotspot_ids
            if course_id not in {course_id for _, course_id in self.prerequisite_plan}
        ]
        capacity_course_count = max(
            1,
            ceil(self.counts["CAPACITY_OVER"] / self.courses[available_hotspot[0]]["capacity"])
        )
        self.capacity_course_ids = available_hotspot[:capacity_course_count]
        cursor = capacity_course_count

        duplicate_course_count = max(
            1,
            ceil(self.counts["DUPLICATE"] / self.courses[available_hotspot[cursor]]["capacity"])
        )
        self.duplicate_course_ids = available_hotspot[cursor:cursor + duplicate_course_count]
        cursor += duplicate_course_count

        time_course_count = max(
            1,
            ceil(self.counts["TIME_CONFLICT"] / self.scenario["course"]["normal_capacity"])
        )
        self.time_conflict_course_ids = available_hotspot[cursor:cursor + time_course_count]
        if len(self.time_conflict_course_ids) != time_course_count:
            raise RuntimeError("not enough disjoint hotspot courses for failure scenarios")

        excluded_hotspot = (
            set(self.capacity_course_ids)
            | set(self.duplicate_course_ids)
            | set(self.time_conflict_course_ids)
            | {course_id for _, course_id in self.prerequisite_plan}
        )
        self.safe_hotspot_ids = [
            course_id for course_id in self.safe_hotspot_ids if course_id not in excluded_hotspot
        ]

        time_seed_by_target = self._find_time_seed_courses(self.time_conflict_course_ids)
        time_seed_course_ids = set(time_seed_by_target.values())
        self.safe_normal_ids = [
            course_id for course_id in self.safe_normal_ids if course_id not in time_seed_course_ids
        ]

        self.capacity_plan = []
        for index, student_id in enumerate(self.capacity_students):
            course_id = self._find_allowed_course(
                student_id,
                self.capacity_course_ids,
                start_index=index
            )
            self.capacity_plan.append((student_id, course_id))

        if not self.seed_filler_students:
            raise RuntimeError("CAPACITY_OVER requires seed-only filler students")
        seed_index = 0
        for course_id in self.capacity_course_ids:
            for _ in range(self.courses[course_id]["capacity"]):
                student_id = self.seed_filler_students[seed_index % len(self.seed_filler_students)]
                seed_index += 1
                self._append_seed_enrollment(student_id, course_id)

        self.duplicate_plan = []
        for index, student_id in enumerate(self.duplicate_students):
            course_id = self._find_allowed_course(
                student_id,
                self.duplicate_course_ids,
                start_index=index
            )
            self._append_seed_enrollment(student_id, course_id)
            self.duplicate_plan.append((student_id, course_id))

        self.time_conflict_plan = []
        time_seed_counts = Counter()
        for index, student_id in enumerate(self.time_conflict_students):
            target_course_id = self._find_time_conflict_target(
                student_id=student_id,
                target_course_ids=self.time_conflict_course_ids,
                seed_course_by_target=time_seed_by_target,
                seed_counts=time_seed_counts,
                start_index=index,
            )
            seed_course_id = time_seed_by_target[target_course_id]
            self._append_seed_enrollment(student_id, seed_course_id)
            time_seed_counts[seed_course_id] += 1
            self.time_conflict_plan.append((student_id, target_course_id))

        seed_counts = Counter(row["course_id"] for row in self.context.data["enrollment"])
        for course_id, count in seed_counts.items():
            if count > self.courses[course_id]["capacity"]:
                raise RuntimeError(
                    f"seed enrollment exceeds capacity: course_id={course_id}, "
                    f"seed={count}, capacity={self.courses[course_id]['capacity']}"
                )
            self.courses[course_id]["current_count"] = count
        self.context.metadata["seed_enrollment_count"] = len(self.context.data["enrollment"])
        self.context.metadata["scenario_course_ids"] = {
            "SUCCESS_HOTSPOT": set(self.safe_hotspot_ids),
            "SUCCESS_NORMAL": set(self.safe_normal_ids),
            "DUPLICATE": set(self.duplicate_course_ids),
            "TIME_CONFLICT": set(self.time_conflict_course_ids),
            "CAPACITY_OVER": set(self.capacity_course_ids),
            "PREREQUISITE_FAIL": {course_id for _, course_id in self.prerequisite_plan},
        }

    def _find_time_seed_courses(self, target_course_ids):
        result = {}
        used = set()
        for target_course_id in target_course_ids:
            target_time = self.course_times[target_course_id]
            seed_course_id = next(
                (
                    course_id
                    for course_id in self.safe_normal_ids
                    if course_id not in used
                    and self._overlaps(target_time, self.course_times[course_id])
                ),
                None,
            )
            if seed_course_id is None:
                raise RuntimeError(f"no independent seed course overlaps TIME_CONFLICT target={target_course_id}")
            result[target_course_id] = seed_course_id
            used.add(seed_course_id)
        return result

    def _find_allowed_course(self, student_id, course_ids, start_index):
        for offset in range(len(course_ids)):
            course_id = course_ids[(start_index + offset) % len(course_ids)]
            if course_id not in self.completed[student_id]:
                return course_id
        raise RuntimeError(f"student_id={student_id} has completed every course in scenario pool")

    def _find_time_conflict_target(
            self,
            student_id,
            target_course_ids,
            seed_course_by_target,
            seed_counts,
            start_index,
    ):
        for offset in range(len(target_course_ids)):
            target_course_id = target_course_ids[(start_index + offset) % len(target_course_ids)]
            seed_course_id = seed_course_by_target[target_course_id]
            if target_course_id in self.completed[student_id]:
                continue
            if seed_counts[seed_course_id] >= self.courses[seed_course_id]["capacity"]:
                continue
            return target_course_id
        raise RuntimeError(
            f"no TIME_CONFLICT target with remaining seed capacity for student_id={student_id}"
        )

    def _append_seed_enrollment(self, student_id, course_id):
        enrollment = self.context.data["enrollment"]
        pair = (student_id, course_id)
        if pair in self.seed_enrollment_pairs:
            raise RuntimeError(f"duplicate seed enrollment student_id={student_id}, course_id={course_id}")
        self.seed_enrollment_pairs.add(pair)
        enrollment.append({
            "id": len(enrollment) + 1,
            "student_id": student_id,
            "course_id": course_id,
            **AUDIT_NULLS,
        })

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
