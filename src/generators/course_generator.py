from .base import AUDIT_NULLS, Generator


class CourseGenerator(Generator):
    table = "course"

    def generate(self, context):
        scenario = context.scenario
        count = scenario["scale"]["courses"]
        hotspot_count = round(count * scenario["traffic"]["hotspot_course_ratio"])
        context.metadata["hotspot_course_ids"] = set(range(1, hotspot_count + 1))
        popular_capacity = scenario["course"]["popular_capacity"]
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

