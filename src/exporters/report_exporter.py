class ReportExporter:
    def export(self, path, title, results):
        path.parent.mkdir(parents=True, exist_ok=True)
        passed = all(result["passed"] for result in results)
        lines = [f"# {title}", "", f"Overall: **{'PASS' if passed else 'FAIL'}**", "", "| Result | Rule | Detail |", "|---|---|---|"]
        for result in results:
            status = "PASS" if result["passed"] else "FAIL"
            detail = str(result["detail"]).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {status} | {result['rule']} | {detail} |")
        lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")

    def export_analysis_reports(self, context, analysis, chart_results=None):
        report_dir = context.output_dir / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        self._hotspot(report_dir / "hotspot_report.md", analysis["hotspot"])
        self._prerequisite(report_dir / "prerequisite_report.md", analysis["prerequisite"])
        self._schedule(report_dir / "schedule_report.md", analysis["schedule"])
        self._credit(report_dir / "credit_report.md", analysis["credit"])
        self._distribution(report_dir / "distribution_report.md", analysis["distribution"])
        self._summary(report_dir / "summary_report.md", context, analysis, chart_results or [])

    @staticmethod
    def _write(path, lines):
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _hotspot(self, path, metric):
        passed = abs(metric["request_ratio"] - metric["expected_request_ratio"]) <= 0.02 and metric["course_ratio"] == metric["expected_course_ratio"]
        self._write(path, [
            "# Hotspot Validation", "",
            f"Result: **{'PASS' if passed else 'FAIL'}**", "",
            "| Metric | Expected | Actual |", "|---|---:|---:|",
            f"| Total courses | {metric['course_total']:,} | {metric['course_total']:,} |",
            f"| Hotspot courses | {metric['expected_course_ratio']:.2%} | {metric['hotspot_course_count']:,} ({metric['course_ratio']:.2%}) |",
            f"| Total requests | {metric['request_total']:,} | {metric['request_total']:,} |",
            f"| Hotspot requests | {metric['expected_request_ratio']:.2%} | {metric['hotspot_request_count']:,} ({metric['request_ratio']:.2%}) |",
            "", "## Performance-test design charts", "",
            "![Course request rank](../charts/course_request_rank_distribution.png)", "",
            "![Hotspot competition](../charts/hotspot_competition.png)", "",
            "![Capacity utilization](../charts/course_capacity_utilization.png)",
        ])

    def _prerequisite(self, path, metric):
        failed = metric["invalid_count"]
        lines = [
            "# Prerequisite Validation", "",
            f"Result: **{'PASS' if failed == 0 else 'FAIL'}**", "",
            f"- Students scanned: {metric['students_scanned']:,}",
            f"- Rules checked: {metric['rules_checked']:,}",
            f"- PREREQUISITE_FAIL payloads checked: {metric['target_requests']:,}",
            f"- Correctly constructed failure cases: {metric['correct_failure_cases']:,}",
            f"- Invalid cases: {failed:,}", "",
            "Validation is request-scoped: the student's department-specific required course must exist and must be absent from completed courses.", "",
        ]
        if metric["invalid_samples"]:
            lines.extend(["## Failure samples", ""] + [f"- student={row['student_id']}, course={row['course_id']}" for row in metric["invalid_samples"]] + [""])
        lines.append("![Prerequisite validation](../charts/prerequisite_validation.png)")
        self._write(path, lines)

    def _schedule(self, path, metric):
        failed = metric["invalid_count"]
        lines = [
            "# Schedule Validation", "",
            f"Result: **{'PASS' if metric['baseline_conflicts'] == 0 and failed == 0 else 'FAIL'}**", "",
            f"- Students checked: {metric['students_checked']:,}",
            f"- Baseline enrollments: {metric['baseline_enrollment_count']:,}",
            f"- Baseline conflicts: {metric['baseline_conflicts']:,}",
            f"- TIME_CONFLICT payloads checked: {metric['target_requests']:,}",
            f"- Correctly constructed conflict cases: {metric['correct_conflict_cases']:,}",
            f"- Invalid cases: {failed:,}", "",
            "Baseline enrollment is intentionally empty. TIME_CONFLICT verification compares each targeted request with a NORMAL request for the same student.", "",
            "![Timeslot heatmap](../charts/timeslot_heatmap.png)",
        ]
        self._write(path, lines)

    def _credit(self, path, metric):
        self._write(path, [
            "# Credit Validation", "",
            f"Result: **{metric['status']}**", "",
            f"- Configured maximum: {metric['configured_limit']} credits",
            f"- Reason: {metric['reason']}", "",
            "This check must remain N/A until the actual JPA model exposes course credits.",
        ])

    def _distribution(self, path, metric):
        self._write(path, [
            "# Data Distribution Validation", "",
            "## Student year distribution", "",
            "| Derived year | Students |", "|---:|---:|",
            *[f"| {year} | {count:,} |" for year, count in sorted(metric["year_counts"].items())],
            "", f"> Source: {metric['year_source']}", "",
            "## Department distribution", "",
            f"- Departments: {len(metric['department_counts']):,}",
            f"- Minimum students per department: {min(metric['department_counts'].values()):,}",
            f"- Maximum students per department: {max(metric['department_counts'].values()):,}", "",
            "The following population charts are supporting evidence rather than the main performance-test narrative.", "",
            "![Student year distribution](../charts/appendix/student_year_distribution.png)", "",
            "![Department distribution](../charts/appendix/department_distribution.png)",
        ])

    def _summary(self, path, context, analysis, chart_results):
        domain_failures = sum(not item["passed"] for item in analysis["domain_results"])
        payload_failures = sum(not item["passed"] for item in analysis["payload_results"])
        prerequisite_failures = analysis["prerequisite"]["invalid_count"]
        schedule_failures = analysis["schedule"]["invalid_count"]
        total_failures = domain_failures + payload_failures + prerequisite_failures + schedule_failures
        lines = [
            "# Mock Data Harness Summary", "",
            f"Overall: **{'PASS' if total_failures == 0 else 'FAIL'}**", "",
            "## Generated scale", "",
            "| Dataset | Rows |", "|---|---:|",
            *[f"| `{name}` | {len(rows):,} |" for name, rows in context.data.items()], "",
            "## Validation results", "",
            f"- Domain validation failures: {domain_failures}",
            f"- Payload validation failures: {payload_failures}",
            f"- Invalid prerequisite scenarios: {prerequisite_failures}",
            f"- Invalid time-conflict scenarios: {schedule_failures}",
            f"- Credit validation: {analysis['credit']['status']}",
            f"- Total actionable failures: {total_failures}", "",
            "## Key distributions", "",
            f"- Hotspot courses: {analysis['hotspot']['hotspot_course_count']:,}/{analysis['hotspot']['course_total']:,} ({analysis['hotspot']['course_ratio']:.2%})",
            f"- Hotspot requests: {analysis['hotspot']['hotspot_request_count']:,}/{analysis['hotspot']['request_total']:,} ({analysis['hotspot']['request_ratio']:.2%})",
            f"- Prerequisite failure scenarios verified: {analysis['prerequisite']['correct_failure_cases']:,}",
            f"- Time-conflict scenarios verified: {analysis['schedule']['correct_conflict_cases']:,}", "",
            "## Reports", "",
            "- [Core validation](validation_report.md)",
            "- [Payload validation](payload_report.md)",
            "- [Hotspot](hotspot_report.md)",
            "- [Prerequisite](prerequisite_report.md)",
            "- [Schedule](schedule_report.md)",
            "- [Credit](credit_report.md)",
            "- [Distribution](distribution_report.md)", "",
            "## Portfolio charts", "",
        ]
        for chart in chart_results:
            lines.extend([
                f"### {chart['title']}", "",
                f"- 파일: `{chart['filename']}`",
                f"- 목적: {chart['purpose']}",
                f"- 해석: {chart['interpretation']}",
                f"- 결과: **{chart['status']}**", "",
                f"![{chart['title']}](../charts/{chart['filename']})", "",
            ])
        lines.extend([
            "## Appendix: population distribution", "",
            "![Student year distribution](../charts/appendix/student_year_distribution.png)", "",
            "![Department distribution](../charts/appendix/department_distribution.png)",
        ])
        self._write(path, lines)
