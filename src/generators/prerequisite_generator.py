from .base import AUDIT_NULLS, Generator


class PrerequisiteGenerator(Generator):
    table = "prerequisite"

    def generate(self, context):
        course_count = context.scenario["scale"]["courses"]
        department_count = context.scenario["scale"]["departments"]
        ratio = context.scenario["scale"]["prerequisite_course_ratio"]
        count = min(course_count - 1, round(course_count * ratio))
        # course_id is always greater than pre_course_id, making cycles impossible.
        course_ids = [2 + (index * (course_count - 2) // count) for index in range(count)]
        context.data[self.table] = [
            {
                "id": index,
                "course_id": course_id,
                "pre_course_id": course_id - (1 + (index % min(50, course_id - 1))),
                "department_id": ((index - 1) % department_count) + 1,
                **AUDIT_NULLS,
            }
            for index, course_id in enumerate(course_ids, 1)
        ]
