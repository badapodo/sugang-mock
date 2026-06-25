from .base import AUDIT_NULLS, Generator


class CourseGenerator(Generator):
    table = "course"

    def generate(self, context):
        scenario = context.scenario
        count = scenario["scale"]["courses"]
        hotspot_count = round(count * scenario["traffic"]["hotspot_course_ratio"])
        context.metadata["hotspot_course_ids"] = set(range(1, hotspot_count + 1))
        popular_capacity = self._popular_capacity(context, hotspot_count)
        scenario["course"]["popular_capacity"] = popular_capacity
        normal_capacity = scenario["course"]["normal_capacity"]
        context.data[self.table] = [
            {
                "id": i,
                "title": f"Course {i:04d}",
                "capacity": popular_capacity if i <= hotspot_count else normal_capacity,
                "current_count": 0,
                "version": 0,
                **AUDIT_NULLS,
            }
            for i in range(1, count + 1)
        ]

    @staticmethod
    def _popular_capacity(context, hotspot_count):
        configured = context.scenario["course"]["popular_capacity"]
        payload = context.scenario.get("payload", {})
        total = payload.get("total_requests", 0)
        if not total or not hotspot_count:
            return configured

        target_hotspot_requests = round(total * context.scenario["traffic"]["hotspot_request_ratio"])
        failure_requests = (
            round(total * payload.get("capacity_over_ratio", 0))
            + round(total * payload.get("duplicate_ratio", 0))
            + round(total * payload.get("prerequisite_fail_ratio", 0))
            + round(total * payload.get("time_conflict_ratio", 0))
        )
        required_hotspot_success = max(0, target_hotspot_requests - failure_requests)
        # Keep a subset of hotspot courses fillable for CAPACITY_OVER while leaving
        # spare hotspot courses for TIME_CONFLICT / PREREQUISITE_FAIL requests that
        # must not be blocked by capacity first.
        fillable_hotspot_courses = max(1, round(hotspot_count * 0.64))
        required_capacity = (required_hotspot_success + fillable_hotspot_courses - 1) // fillable_hotspot_courses
        return max(configured, required_capacity)
