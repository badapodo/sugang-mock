from datetime import datetime, timedelta

from .base import AUDIT_NULLS, Generator


class CourseTimeGenerator(Generator):
    table = "course_time"

    def generate(self, context):
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        # 90-minute classes ending by 17:00. Repeated slots act as deterministic
        # weights and create realistic late-morning / early-afternoon peaks.
        weighted_start_minutes = (
            [9 * 60, 9 * 60 + 30]
            + [10 * 60, 10 * 60 + 30, 11 * 60, 11 * 60 + 30] * 4
            + [12 * 60, 12 * 60 + 30]
            + [13 * 60, 13 * 60 + 30, 14 * 60, 14 * 60 + 30] * 4
            + [15 * 60, 15 * 60 + 30]
        )
        rows = []
        row_id = 1
        per_course = context.scenario["scale"]["course_times_per_course"]
        for course in context.data["course"]:
            for offset in range(per_course):
                start_minutes = context.random.choice(weighted_start_minutes)
                start = datetime(2000, 1, 1) + timedelta(minutes=start_minutes)
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
