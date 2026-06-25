from collections import Counter, defaultdict

from src.generators.payload_generator import allocate_scenario_counts
from .base import result


SUCCESS_SCENARIOS = {"NORMAL", "HOTSPOT"}
FAILURE_SCENARIOS = {"PREREQUISITE_FAIL", "TIME_CONFLICT", "CAPACITY_OVER", "DUPLICATE"}


class PayloadValidator:
    def validate(self, context):
        rows = context.data["enrollment_payload"]
        scenario = context.scenario
        payload = scenario["payload"]
        total = payload["total_requests"]
        results = [result("payload row count", len(rows) == total, f"actual={len(rows)}, expected={total}")]

        hotspot_count = sum(row["course_id"] in context.metadata["hotspot_course_ids"] for row in rows)
        actual_hotspot = hotspot_count / total
        target_hotspot = scenario["traffic"]["hotspot_request_ratio"]
        results.append(result("hotspot request ratio", abs(actual_hotspot - target_hotspot) <= 0.02, f"actual={actual_hotspot:.4f}, target={target_hotspot:.4f}"))

        burst = sum(0 <= row["scheduled_offset_ms"] < 10000 for row in rows)
        tail = sum(10000 <= row["scheduled_offset_ms"] <= 30000 for row in rows)
        target_burst = scenario["traffic"]["burst_window_ratio"]
        valid_offsets = burst + tail == total
        results.append(result("scheduled offset distribution", valid_offsets and abs(burst / total - target_burst) <= 0.02, f"0-10s={burst/total:.4f}, 10-30s={tail/total:.4f}"))

        actual_types = Counter(row["scenario_type"] for row in rows)
        expected_types = allocate_scenario_counts(payload)
        actual_with_zeroes = {name: actual_types.get(name, 0) for name in expected_types}
        results.append(result("scenario type ratios", actual_with_zeroes == expected_types, f"actual={actual_with_zeroes}, expected={expected_types}"))

        student_ids = {row["student_id"] for row in context.data["student"]}
        course_ids = {row["id"] for row in context.data["course"]}
        invalid_refs = [index for index, row in enumerate(rows, 1) if row["student_id"] not in student_ids or row["course_id"] not in course_ids]
        results.append(result("payload references", not invalid_refs, invalid_refs[:10] or "all student/course IDs exist"))

        expected_status = payload["expected_status"]
        invalid_status = [index for index, row in enumerate(rows, 1) if row["expected_status"] != expected_status.get(row["scenario_type"])]
        results.append(result("expected status mapping", not invalid_status, invalid_status[:10] or "all statuses match scenario type"))

        active_count = len({row["student_id"] for row in rows})
        expected_active = scenario["traffic"]["active_users"]
        results.append(result("active users", active_count == expected_active, f"actual={active_count}, expected={expected_active}"))

        integrity = self._validate_payload_semantics(context, rows)
        context.metadata["payload_integrity"] = integrity

        results.extend([
            result("payload duplicate integrity", integrity["payload_duplicate_count"] == 0, f"unexpected success duplicate pairs={integrity['payload_duplicate_count']}"),
            result("normal payload semantics", integrity["invalid_normal_count"] == 0, f"invalid NORMAL/success payloads={integrity['invalid_normal_count']}"),
            result("capacity_over semantics", integrity["invalid_capacity_over_count"] == 0, f"invalid CAPACITY_OVER payloads={integrity['invalid_capacity_over_count']}"),
            result("duplicate scenario semantics", integrity["invalid_duplicate_count"] == 0, f"invalid DUPLICATE payloads={integrity['invalid_duplicate_count']}"),
            result("time_conflict semantics", integrity["invalid_time_conflict_count"] == 0, f"invalid TIME_CONFLICT payloads={integrity['invalid_time_conflict_count']}"),
            result("prerequisite_fail semantics", integrity["invalid_prerequisite_fail_count"] == 0, f"invalid PREREQUISITE_FAIL payloads={integrity['invalid_prerequisite_fail_count']}"),
            result("scenario label consistency", integrity["scenario_label_inconsistency_count"] == 0, f"inconsistent labels={integrity['scenario_label_inconsistency_count']}"),
        ])
        return results

    def _validate_payload_semantics(self, context, rows):
        courses = {row["id"]: row for row in context.data["course"]}
        completed_by_student = context.metadata["completed_by_student"]
        department_by_student = {row["student_id"]: row["department_id"] for row in context.data["student"]}
        prerequisites = defaultdict(list)
        for row in context.data["prerequisite"]:
            prerequisites[(row["course_id"], row["department_id"])].append(row["pre_course_id"])

        time_by_course = {row["course_id"]: row for row in context.data["course_time"]}
        rows_with_ids = [
            {
                "request_id": index,
                **row,
            }
            for index, row in enumerate(rows, 1)
        ]

        duplicate_all = self._duplicates(rows_with_ids)
        unexpected_duplicate_all = self._unexpected_success_duplicates(rows_with_ids)
        ordered_rows = sorted(rows_with_ids, key=lambda row: (row["scheduled_offset_ms"], row["request_id"]))

        accepted_by_student = defaultdict(list)
        accepted_pairs = set()
        accepted_count_by_course = Counter()
        accepted_pair_first_request = {}

        invalid_normal = []
        invalid_capacity_over = []
        invalid_duplicate = []
        invalid_time_conflict = []
        invalid_prerequisite_fail = []
        label_inconsistencies = []

        for row in ordered_rows:
            scenario_type = row["scenario_type"]
            expected_status = str(row["expected_status"])
            student_id = row["student_id"]
            course_id = row["course_id"]
            pair = (student_id, course_id)

            label_reason = self._label_inconsistency(row)
            if label_reason:
                label_inconsistencies.append(self._failure(row, label_reason))

            if self._is_expected_success(row):
                reasons = []
                if course_id in completed_by_student[student_id]:
                    reasons.append("student already completed course")
                if pair in accepted_pairs:
                    first_request = accepted_pair_first_request.get(pair)
                    reasons.append(f"duplicate success pair; first success request_id={first_request}")

                required = prerequisites.get((course_id, department_by_student[student_id]), [])
                missing = [course for course in required if course not in completed_by_student[student_id]]
                if missing:
                    reasons.append(f"missing prerequisite course_id={missing}")

                conflict_course_id = self._find_conflict(course_id, accepted_by_student[student_id], time_by_course)
                if conflict_course_id is not None:
                    reasons.append(f"time conflict with prior success course_id={conflict_course_id}")

                capacity = courses[course_id]["capacity"]
                if accepted_count_by_course[course_id] >= capacity:
                    reasons.append(f"course capacity exceeded before success request; accepted={accepted_count_by_course[course_id]}, capacity={capacity}")

                if reasons:
                    invalid_normal.append(self._failure(row, "; ".join(reasons)))
                    continue

                accepted_by_student[student_id].append(course_id)
                accepted_pairs.add(pair)
                accepted_pair_first_request.setdefault(pair, row["request_id"])
                accepted_count_by_course[course_id] += 1
                continue

            if scenario_type == "CAPACITY_OVER":
                capacity = courses[course_id]["capacity"]
                if accepted_count_by_course[course_id] < capacity:
                    invalid_capacity_over.append(self._failure(row, f"capacity not yet exceeded; accepted_success={accepted_count_by_course[course_id]}, capacity={capacity}"))
                continue

            if scenario_type == "DUPLICATE":
                if pair not in accepted_pairs:
                    invalid_duplicate.append(self._failure(row, "no prior successful request for same student_id/course_id"))
                continue

            if scenario_type == "TIME_CONFLICT":
                conflict_course_id = self._find_conflict(course_id, accepted_by_student[student_id], time_by_course)
                if conflict_course_id is None:
                    reason = "no prior successful course for student" if not accepted_by_student[student_id] else "no overlapping prior successful course"
                    invalid_time_conflict.append(self._failure(row, reason))
                continue

            if scenario_type == "PREREQUISITE_FAIL":
                required = prerequisites.get((course_id, department_by_student[student_id]), [])
                missing = [course for course in required if course not in completed_by_student[student_id]]
                if not required:
                    invalid_prerequisite_fail.append(self._failure(row, "course has no prerequisite rule for student's department"))
                elif not missing:
                    invalid_prerequisite_fail.append(self._failure(row, f"student already satisfies prerequisites={required}"))
                continue

            # Unknown failure-like labels are captured by label consistency and do
            # not participate in success-state simulation.
            _ = expected_status

        integrity = {
            "duplicate_top": duplicate_all[:20],
            "unexpected_duplicate_top": unexpected_duplicate_all[:20],
            "payload_duplicate_count": sum(item["duplicate_count"] for item in unexpected_duplicate_all),
            "invalid_normal": invalid_normal,
            "invalid_capacity_over": invalid_capacity_over,
            "invalid_duplicate": invalid_duplicate,
            "invalid_time_conflict": invalid_time_conflict,
            "invalid_prerequisite_fail": invalid_prerequisite_fail,
            "scenario_label_inconsistencies": label_inconsistencies,
            "invalid_normal_count": len(invalid_normal),
            "invalid_capacity_over_count": len(invalid_capacity_over),
            "invalid_duplicate_count": len(invalid_duplicate),
            "invalid_time_conflict_count": len(invalid_time_conflict),
            "invalid_prerequisite_fail_count": len(invalid_prerequisite_fail),
            "scenario_label_inconsistency_count": len(label_inconsistencies),
        }
        integrity["total_actionable_failures"] = (
            integrity["payload_duplicate_count"]
            + integrity["invalid_normal_count"]
            + integrity["invalid_capacity_over_count"]
            + integrity["invalid_duplicate_count"]
            + integrity["invalid_time_conflict_count"]
            + integrity["invalid_prerequisite_fail_count"]
            + integrity["scenario_label_inconsistency_count"]
        )
        return integrity

    @staticmethod
    def _is_expected_success(row):
        return row["scenario_type"] in SUCCESS_SCENARIOS or str(row["expected_status"]) == "200"

    @staticmethod
    def _label_inconsistency(row):
        scenario_type = row["scenario_type"]
        expected_status = str(row["expected_status"])
        if scenario_type in SUCCESS_SCENARIOS and expected_status != "200":
            return f"{scenario_type} must use expected_status=200"
        if scenario_type in FAILURE_SCENARIOS and not expected_status.startswith("4"):
            return f"{scenario_type} must use expected_status=4xx"
        if scenario_type not in SUCCESS_SCENARIOS | FAILURE_SCENARIOS:
            return f"unknown scenario_type={scenario_type}"
        return None

    def _unexpected_success_duplicates(self, rows):
        success_rows = [row for row in rows if self._is_expected_success(row)]
        return self._duplicates(success_rows)

    @staticmethod
    def _duplicates(rows):
        pair_to_requests = defaultdict(list)
        pair_to_scenarios = defaultdict(Counter)
        for row in rows:
            pair = (row["student_id"], row["course_id"])
            pair_to_requests[pair].append(row["request_id"])
            pair_to_scenarios[pair][row["scenario_type"]] += 1
        duplicates = []
        for (student_id, course_id), request_ids in pair_to_requests.items():
            if len(request_ids) <= 1:
                continue
            duplicates.append({
                "student_id": student_id,
                "course_id": course_id,
                "count": len(request_ids),
                "duplicate_count": len(request_ids) - 1,
                "request_ids": request_ids[:10],
                "scenario_counts": dict(pair_to_scenarios[(student_id, course_id)]),
            })
        duplicates.sort(key=lambda item: (-item["count"], item["student_id"], item["course_id"]))
        return duplicates

    @staticmethod
    def _find_conflict(course_id, prior_course_ids, time_by_course):
        selected = time_by_course.get(course_id)
        if selected is None:
            return None
        for prior_course_id in prior_course_ids:
            prior = time_by_course.get(prior_course_id)
            if prior and PayloadValidator._overlaps(selected, prior):
                return prior_course_id
        return None

    @staticmethod
    def _overlaps(left, right):
        return (
            left["day_of_week"] == right["day_of_week"]
            and left["start_time"] < right["end_time"]
            and right["start_time"] < left["end_time"]
        )

    @staticmethod
    def _failure(row, reason):
        return {
            "request_id": row["request_id"],
            "student_id": row["student_id"],
            "course_id": row["course_id"],
            "scenario_type": row["scenario_type"],
            "expected_status": row["expected_status"],
            "scheduled_offset_ms": row["scheduled_offset_ms"],
            "reason": reason,
        }
