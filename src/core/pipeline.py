from __future__ import annotations

from src.analyzers import ValidationAnalyzer
from src.exporters import ChartExporter, CopySqlExporter, CsvExporter, ReportExporter
from src.generators import (
    CompletedCourseGenerator,
    CourseGenerator,
    CourseTimeGenerator,
    DepartmentGenerator,
    MemberGenerator,
    PrerequisiteGenerator,
    StudentGenerator,
)
from src.generators.payload_generator import PayloadGenerator
from src.validators import DomainValidator, PayloadValidator
from src.validators.base import ValidationError


class Pipeline:
    def __init__(self):
        self.domain_generators = [
            DepartmentGenerator(),
            MemberGenerator(),
            CourseGenerator(),
            StudentGenerator(),
            CourseTimeGenerator(),
            PrerequisiteGenerator(),
            CompletedCourseGenerator(),
        ]
        self.csv_exporter = CsvExporter()
        self.sql_exporter = CopySqlExporter()
        self.report_exporter = ReportExporter()
        self.chart_exporter = ChartExporter()

    def run(self, context):
        print("[1/8] Analyze schema-map")
        self._validate_contract(context)

        print("[2/8] Generate domain data")
        for generator in self.domain_generators:
            generator.generate(context)
        context.data["enrollment"] = []

        print("[3/8] Generate k6 payload")
        PayloadGenerator().generate(context)

        print("[4/8] Validate generated data")
        domain_results = DomainValidator().validate(context)
        payload_results = PayloadValidator().validate(context)
        validation_path = context.output_dir / "reports" / "validation_report.md"
        self.report_exporter.export(validation_path, "Domain Data Validation Report", domain_results)
        payload_path = context.output_dir / "reports" / "payload_report.md"
        self.report_exporter.export(payload_path, "Payload Validation Report", payload_results)

        print("[5/8] Analyze validation metrics")
        analysis = ValidationAnalyzer().analyze(context, domain_results, payload_results)

        print("[6/8] Export CSV and PostgreSQL COPY SQL")
        self.csv_exporter.export(context)
        self.csv_exporter.export_payload(context)
        self.sql_exporter.export(context)

        print("[7/8] Generate Markdown reports")
        self.report_exporter.export_analysis_reports(context, analysis)

        print("[8/8] Generate visualization charts")
        self.chart_exporter.export(context, analysis)

        self._require_pass(domain_results, validation_path)
        self._require_pass(payload_results, payload_path)
        self._require_analysis(analysis, context.output_dir / "reports" / "summary_report.md")

        print("\nDONE")
        print(f"- {context.output_dir / 'csv'}/*.csv")
        print(f"- {context.output_dir / 'sql' / 'load.sql'}")
        print(f"- {context.output_dir / 'reports' / 'validation_report.md'}")
        print(f"- {context.output_dir / 'reports' / 'payload_report.md'}")
        print(f"- {context.output_dir / 'reports' / 'summary_report.md'}")
        print(f"- {context.output_dir / 'charts'}/*.png")

    @staticmethod
    def _validate_contract(context):
        tables = set(context.schema["tables"])
        load_order = context.schema["copy"]["load_order"]
        if set(load_order) != tables or len(load_order) != len(tables):
            raise ValueError("schema-map copy.load_order must contain every table exactly once")
        for table_name, table in context.schema["tables"].items():
            if not table.get("csv") or not table.get("columns"):
                raise ValueError(f"schema-map table {table_name} needs csv and columns")

    @staticmethod
    def _require_pass(results, report_path):
        failures = [item for item in results if not item["passed"]]
        if failures:
            rules = ", ".join(item["rule"] for item in failures)
            raise ValidationError(f"Validation failed ({rules}). See {report_path}")

    @staticmethod
    def _require_analysis(analysis, report_path):
        failures = analysis["prerequisite"]["invalid_count"] + analysis["schedule"]["invalid_count"]
        if failures:
            raise ValidationError(f"Semantic scenario validation failed ({failures} cases). See {report_path}")
