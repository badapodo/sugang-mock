from pathlib import Path


class CopySqlExporter:
    def export(self, context):
        sql_dir = context.output_dir / "sql"
        sql_dir.mkdir(parents=True, exist_ok=True)
        cleanup = context.schema["copy"]["cleanup_order"]
        load_order = context.schema["copy"]["load_order"]
        null_value = context.schema["copy"].get("null_value", "\\N")

        truncate = "TRUNCATE TABLE " + ", ".join(cleanup) + " RESTART IDENTITY CASCADE;\n"
        (sql_dir / "truncate.sql").write_text(truncate, encoding="utf-8")

        lines = ["\\set ON_ERROR_STOP on", "BEGIN;", "\\ir truncate.sql", ""]
        for table_name in load_order:
            table = context.table(table_name)
            columns = ", ".join(column["name"] for column in table["columns"])
            csv_path = Path("output/csv") / table["csv"]
            lines.append(
                f"\\copy {table_name} ({columns}) FROM '{csv_path}' "
                f"WITH (FORMAT csv, HEADER true, NULL '{null_value}');"
            )

        lines.extend(["", "-- Keep identity generators ahead of explicitly copied primary keys."])
        for table_name in load_order:
            table = context.table(table_name)
            for pk in table.get("primary_key", []):
                column = next(item for item in table["columns"] if item["name"] == pk)
                if column.get("jpa_generation") == "identity":
                    lines.append(
                        "SELECT setval(pg_get_serial_sequence(" +
                        f"'{table_name}', '{pk}'), COALESCE(MAX({pk}), 0) + 1, false) FROM {table_name};"
                    )
        lines.extend(["", "COMMIT;", ""])
        (sql_dir / "load.sql").write_text("\n".join(lines), encoding="utf-8")

