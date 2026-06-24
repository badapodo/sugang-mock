from collections import Counter

from src.generators.payload_generator import allocate_scenario_counts
from .base import result


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
        return results
