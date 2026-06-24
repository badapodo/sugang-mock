from .base import AUDIT_NULLS, Generator


class DepartmentGenerator(Generator):
    table = "department"

    def generate(self, context):
        count = context.scenario["scale"]["departments"]
        context.data[self.table] = [
            {"id": i, "name": f"Department {i:03d}", **AUDIT_NULLS}
            for i in range(1, count + 1)
        ]

