from collections import defaultdict
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
        scenario = context.scenario
        payload_config = scenario["payload"]
        total = payload_config["total_requests"]
        counts = allocate_scenario_counts(payload_config)
        if sum(payload_config.get(key, 0) for key in SCENARIO_RATIO_KEYS.values()) != 1:
            raise ValueError("payload scenario ratios must sum to 1.0")

        scenario_types = [name for name, count in counts.items() for _ in range(count)]
        context.random.shuffle(scenario_types)
        hotspot_count = round(total * scenario["traffic"]["hotspot_request_ratio"])
        hotspot_flags = [True] * hotspot_count + [False] * (total - hotspot_count)
        context.random.shuffle(hotspot_flags)

        burst_count = round(total * scenario["traffic"]["burst_window_ratio"])
        offsets = [context.random.randint(0, 9999) for _ in range(burst_count)]
        offsets += [context.random.randint(10000, 30000) for _ in range(total - burst_count)]
        context.random.shuffle(offsets)

        all_students = [row["student_id"] for row in context.data["student"]]
        active_count = scenario["traffic"]["active_users"]
        if active_count > len(all_students):
            raise ValueError("traffic.active_users cannot exceed scale.students")
        active_students = context.random.sample(all_students, active_count)
        context.metadata["active_student_ids"] = set(active_students)
        student_queue = (active_students * ((total + active_count - 1) // active_count))[:total]
        context.random.shuffle(student_queue)

        hotspot_ids = sorted(context.metadata["hotspot_course_ids"])
        normal_ids = [row["id"] for row in context.data["course"] if row["id"] not in context.metadata["hotspot_course_ids"]]
        prerequisite_course_ids = {row["course_id"] for row in context.data["prerequisite"]}
        safe_hotspot = [course_id for course_id in hotspot_ids if course_id not in prerequisite_course_ids] or hotspot_ids
        safe_normal = [course_id for course_id in normal_ids if course_id not in prerequisite_course_ids] or normal_ids

        students_by_department = defaultdict(list)
        departments_by_student = {}
        active_set = set(active_students)
        for student in context.data["student"]:
            departments_by_student[student["student_id"]] = student["department_id"]
            if student["student_id"] in active_set:
                students_by_department[student["department_id"]].append(student["student_id"])
        completed = context.metadata["completed_by_student"]
        rules_by_hotspot = {True: [], False: []}
        for rule in context.data["prerequisite"]:
            candidates = [sid for sid in students_by_department[rule["department_id"]] if rule["pre_course_id"] not in completed[sid]]
            if candidates:
                rules_by_hotspot[rule["course_id"] in context.metadata["hotspot_course_ids"]].append((rule, candidates))

        prior_pairs = {True: [], False: []}
        normal_courses_by_student = defaultdict(list)
        rows = []
        expected_status = payload_config["expected_status"]
        for index, (scenario_type, is_hotspot, offset) in enumerate(zip(scenario_types, hotspot_flags, offsets)):
            student_id = student_queue[index]
            pool = hotspot_ids if is_hotspot else normal_ids
            safe_pool = safe_hotspot if is_hotspot else safe_normal

            if scenario_type == "DUPLICATE" and prior_pairs[is_hotspot]:
                student_id, course_id = context.random.choice(prior_pairs[is_hotspot])
            elif scenario_type == "PREREQUISITE_FAIL" and rules_by_hotspot[is_hotspot]:
                rule, candidates = context.random.choice(rules_by_hotspot[is_hotspot])
                student_id = context.random.choice(candidates)
                course_id = rule["course_id"]
            elif scenario_type == "TIME_CONFLICT" and normal_courses_by_student[student_id]:
                base_course = context.random.choice(normal_courses_by_student[student_id])
                base_time = next(row for row in context.data["course_time"] if row["course_id"] == base_course)
                collisions = [
                    row["course_id"] for row in context.data["course_time"]
                    if row["day_of_week"] == base_time["day_of_week"]
                    and row["start_time"] < base_time["end_time"]
                    and base_time["start_time"] < row["end_time"]
                    and (row["course_id"] in context.metadata["hotspot_course_ids"]) == is_hotspot
                    and row["course_id"] != base_course
                ]
                course_id = context.random.choice(collisions or pool)
            elif scenario_type == "NORMAL":
                course_id = context.random.choice(safe_pool)
                normal_courses_by_student[student_id].append(course_id)
            else:
                course_id = context.random.choice(pool)

            prior_pairs[is_hotspot].append((student_id, course_id))
            rows.append({
                "student_id": student_id,
                "course_id": course_id,
                "scenario_type": scenario_type,
                "expected_status": expected_status[scenario_type],
                "scheduled_offset_ms": offset,
            })
        self._guarantee_time_conflicts(context, rows)

        # Scenario-specific selection can replace the queued student. Repair coverage
        # after semantic construction so exactly the configured active users remain.
        present = {row["student_id"] for row in rows}
        missing = [student_id for student_id in active_students if student_id not in present]
        replaceable = [row for row in rows if row["scenario_type"] in {"CAPACITY_OVER", "CREDIT_LIMIT"}]
        for student_id, row in zip(missing, replaceable):
            row["student_id"] = student_id
        context.data[self.table] = rows

    @staticmethod
    def _guarantee_time_conflicts(context, rows):
        time_by_course = {row["course_id"]: row for row in context.data["course_time"]}
        courses_by_signature = defaultdict(lambda: {True: [], False: []})
        hotspots = context.metadata["hotspot_course_ids"]
        for course_id, course_time in time_by_course.items():
            signature = (course_time["day_of_week"], course_time["start_time"], course_time["end_time"])
            courses_by_signature[signature][course_id in hotspots].append(course_id)

        normal_by_student = defaultdict(list)
        for row in rows:
            if row["scenario_type"] == "NORMAL":
                normal_by_student[row["student_id"]].append(row["course_id"])

        anchors = []
        for student_id, course_ids in normal_by_student.items():
            for course_id in course_ids:
                course_time = time_by_course[course_id]
                signature = (course_time["day_of_week"], course_time["start_time"], course_time["end_time"])
                anchors.append((student_id, course_id, signature))

        for row in rows:
            if row["scenario_type"] != "TIME_CONFLICT":
                continue
            is_hotspot = row["course_id"] in hotspots
            candidates = []
            for base_course in normal_by_student.get(row["student_id"], []):
                base_time = time_by_course[base_course]
                signature = (base_time["day_of_week"], base_time["start_time"], base_time["end_time"])
                collisions = [course_id for course_id in courses_by_signature[signature][is_hotspot] if course_id != base_course]
                if collisions:
                    candidates.append((row["student_id"], collisions))
            if not candidates:
                for student_id, base_course, signature in anchors:
                    collisions = [course_id for course_id in courses_by_signature[signature][is_hotspot] if course_id != base_course]
                    if collisions:
                        candidates.append((student_id, collisions))
                        if len(candidates) >= 100:
                            break
            student_id, collisions = context.random.choice(candidates)
            row["student_id"] = student_id
            row["course_id"] = context.random.choice(collisions)
