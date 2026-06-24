from .base import AUDIT_NULLS, Generator


class StudentGenerator(Generator):
    table = "student"

    def generate(self, context):
        count = context.scenario["scale"]["students"]
        departments = context.scenario["scale"]["departments"]
        context.data[self.table] = [
            {
                "student_id": i,
                "department_id": ((i - 1) % departments) + 1,
                "member_id": i,
                **AUDIT_NULLS,
            }
            for i in range(1, count + 1)
        ]

