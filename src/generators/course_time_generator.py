from datetime import datetime, timedelta

from .base import AUDIT_NULLS, Generator


class CourseTimeGenerator(Generator):
    table = "course_time"

    def generate(self, context):
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        rows = []
        row_id = 1
        per_course = context.scenario["scale"]["course_times_per_course"]
        for course in context.data["course"]:
            for offset in range(per_course):
                slot = (course["id"] * 7 + offset * 3) % 16
                start = datetime(2000, 1, 1, 9, 0) + timedelta(minutes=slot * 30)
                end = start + timedelta(minutes=90)
                rows.append({
                    "id": row_id,
                    "course_id": course["id"],
                    "day_of_week": days[(course["id"] + offset) % len(days)],
                    "start_time": start.strftime("%H:%M:%S"),
                    "end_time": end.strftime("%H:%M:%S"),
                    "location": f"R{((course['id'] - 1) % 200) + 1:03d}",
                    **AUDIT_NULLS,
                })
                row_id += 1
        context.data[self.table] = rows

