import csv


class CsvExporter:
    def export(self, context, tables=None):
        csv_dir = context.output_dir / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)
        tables = tables or context.schema["copy"]["load_order"]
        null_value = context.schema["copy"].get("null_value", "\\N")
        for table_name in tables:
            table = context.table(table_name)
            columns = [column["name"] for column in table["columns"]]
            path = csv_dir / table["csv"]
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=columns,
                    extrasaction="ignore",
                    lineterminator="\n",
                )
                writer.writeheader()
                for row in context.data.get(table_name, []):
                    writer.writerow({key: null_value if row.get(key) is None else row.get(key) for key in columns})

    def export_payload(self, context):
        csv_dir = context.output_dir / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)
        columns = ["student_id", "course_id", "scenario_type", "expected_status", "scheduled_offset_ms"]
        with (csv_dir / "enrollment_payload.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(context.data["enrollment_payload"])
