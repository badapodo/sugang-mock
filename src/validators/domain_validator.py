from collections import Counter, defaultdict
from datetime import time

from .base import result


class DomainValidator:
    def validate(self, context):
        scenario = context.scenario
        expected = {
            "department": scenario["scale"]["departments"],
            "member": scenario["scale"]["students"],
            "student": scenario["scale"]["students"],
            "course": scenario["scale"]["courses"],
            "course_time": scenario["scale"]["courses"] * scenario["scale"]["course_times_per_course"],
            "prerequisite": round(scenario["scale"]["courses"] * scenario["scale"]["prerequisite_course_ratio"]),
            "completed_course": scenario["scale"]["students"] * scenario["scale"]["avg_courses_per_student"],
            "enrollment": 0,
        }
        results = []
        mismatches = {name: (len(context.data.get(name, [])), count) for name, count in expected.items() if len(context.data.get(name, [])) != count}
        results.append(result("table row counts", not mismatches, mismatches or "all counts match scenario"))

        missing = []
        duplicates = []
        unique_failures = []
        for table_name, table in context.schema["tables"].items():
            rows = context.data.get(table_name, [])
            required = [column["name"] for column in table["columns"] if not column.get("nullable", True) or column.get("domain_required")]
            for row_index, row in enumerate(rows, 1):
                for column in required:
                    if row.get(column) in {None, ""}:
                        missing.append(f"{table_name}[{row_index}].{column}")
                        if len(missing) >= 10:
                            break
            for columns in [table.get("primary_key", [])] + [u["columns"] for u in table.get("unique_constraints", [])]:
                seen = set()
                for row in rows:
                    key = tuple(row.get(column) for column in columns)
                    if key in seen:
                        target = duplicates if columns == table.get("primary_key", []) else unique_failures
                        target.append(f"{table_name}{tuple(columns)}={key}")
                        break
                    seen.add(key)
        results.append(result("required columns", not missing, missing or "no null/empty required values"))
        results.append(result("primary keys", not duplicates, duplicates or "all primary keys unique"))
        results.append(result("unique constraints", not unique_failures, unique_failures or "all configured unique keys unique"))

        fk_failures = []
        for table_name, table in context.schema["tables"].items():
            for column in table["columns"]:
                fk = column.get("foreign_key")
                if not fk:
                    continue
                target = {row[fk["column"]] for row in context.data[fk["table"]]}
                invalid = [row[column["name"]] for row in context.data[table_name] if row.get(column["name"]) is not None and row[column["name"]] not in target]
                if invalid:
                    fk_failures.append(f"{table_name}.{column['name']} -> {fk['table']}.{fk['column']}: {invalid[:5]}")
        results.append(result("physical and logical foreign keys", not fk_failures, fk_failures or "all references resolve"))

        expected_hotspots = round(scenario["scale"]["courses"] * scenario["traffic"]["hotspot_course_ratio"])
        actual_hotspots = len(context.metadata["hotspot_course_ids"])
        results.append(result("hotspot course ratio", actual_hotspots == expected_hotspots, f"actual={actual_hotspots}, expected={expected_hotspots}"))

        time_failures = []
        for row in context.data["course_time"]:
            start = time.fromisoformat(row["start_time"])
            end = time.fromisoformat(row["end_time"])
            if not (time(9) <= start < end <= time(17)) or start.minute % 30 or end.minute % 30:
                time_failures.append(row["id"])
        results.append(result("course time range", not time_failures, time_failures[:10] or "all times are within 09:00-17:00 and aligned to 30 minutes"))

        completed = context.metadata["completed_by_student"]
        students_by_department = defaultdict(list)
        for student in context.data["student"]:
            students_by_department[student["department_id"]].append(student["student_id"])
        unsatisfied = []
        for rule_row in context.data["prerequisite"]:
            if not any(rule_row["pre_course_id"] in completed[student_id] for student_id in students_by_department[rule_row["department_id"]]):
                unsatisfied.append(rule_row["id"])
        results.append(result("prerequisite satisfiability", not unsatisfied, unsatisfied[:10] or "every rule is satisfiable by a student in its department"))

        course_counts = Counter(row["course_id"] for row in context.data["enrollment"])
        current_mismatch = [row["id"] for row in context.data["course"] if row["current_count"] != course_counts[row["id"]]]
        results.append(result("course current_count", not current_mismatch, current_mismatch[:10] or "matches baseline enrollments"))
        return results
