from .base import AUDIT_NULLS, Generator


class CompletedCourseGenerator(Generator):
    table = "completed_course"

    def generate(self, context):
        course_ids = [row["id"] for row in context.data["course"]]
        avg = context.scenario["scale"]["avg_courses_per_student"]
        completed: dict[int, set[int]] = {
            student["student_id"]: set(context.random.sample(course_ids, avg))
            for student in context.data["student"]
        }

        students_by_department: dict[int, list[int]] = {}
        for student in context.data["student"]:
            students_by_department.setdefault(student["department_id"], []).append(student["student_id"])

        # Every prerequisite can be satisfied by at least one student in its department
        # without changing the configured rows-per-student count.
        for rule_index, rule in enumerate(context.data["prerequisite"]):
            candidates = students_by_department[rule["department_id"]]
            student_id = candidates[rule_index % len(candidates)]
            values = completed[student_id]
            if rule["pre_course_id"] not in values:
                values.remove(max(values))
                values.add(rule["pre_course_id"])

        rows = []
        row_id = 1
        for student_id in sorted(completed):
            for course_id in sorted(completed[student_id]):
                rows.append({
                    "id": row_id,
                    "student_id": student_id,
                    "course_id": course_id,
                    **AUDIT_NULLS,
                })
                row_id += 1
        context.data[self.table] = rows
        context.metadata["completed_by_student"] = completed

