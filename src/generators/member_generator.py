from .base import AUDIT_NULLS, Generator


# BCrypt hash for the common mock password "password". Keeping one valid hash avoids
# an optional bcrypt dependency and deliberately makes this test-only data obvious.
MOCK_PASSWORD_HASH = "$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy"


class MemberGenerator(Generator):
    table = "member"

    def generate(self, context):
        count = context.scenario["scale"]["students"]
        context.data[self.table] = [
            {
                "member_id": i,
                "email": f"student{i:05d}@mock.local",
                "password": MOCK_PASSWORD_HASH,
                "name": f"Student {i:05d}",
                "role": "ROLE_USER",
                **AUDIT_NULLS,
            }
            for i in range(1, count + 1)
        ]

