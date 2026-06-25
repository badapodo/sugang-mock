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
        self.export_payload_integrity_reports(context)
        self._hotspot(report_dir / "hotspot_report.md", analysis["hotspot"])
        self._prerequisite(report_dir / "prerequisite_report.md", analysis["prerequisite"])
        self._schedule(report_dir / "schedule_report.md", analysis["schedule"])
        self._credit(report_dir / "credit_report.md", analysis["credit"])
        self._distribution(report_dir / "distribution_report.md", analysis["distribution"])
        self._summary(report_dir / "summary_report.md", context, analysis, chart_results or [])

    @staticmethod
    def _write(path, lines):
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def export_payload_integrity_reports(self, context):
        report_dir = context.output_dir / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        integrity = context.metadata.get("payload_integrity")
        if not integrity:
            return

        self._payload_integrity(report_dir / "payload_integrity_report.md", integrity)
        self._duplicate_payload(report_dir / "duplicate_payload_report.md", integrity)
        self._failure_samples(
            report_dir / "normal_payload_validation_report.md",
            "NORMAL Payload Validation",
            integrity["invalid_normal"],
            "NORMAL or expected_status=200 payloads must be executable successes before the load test starts.",
        )
        self._failure_samples(
            report_dir / "capacity_over_validation_report.md",
            "CAPACITY_OVER Payload Validation",
            integrity["invalid_capacity_over"],
            "CAPACITY_OVER payloads must arrive only after accepted success requests have filled the course capacity.",
        )
        self._failure_samples(
            report_dir / "duplicate_scenario_validation_report.md",
            "DUPLICATE Scenario Validation",
            integrity["invalid_duplicate"],
            "DUPLICATE payloads must have a prior successful request with the same student_id/course_id pair.",
        )
        self._failure_samples(
            report_dir / "time_conflict_validation_report.md",
            "TIME_CONFLICT Payload Validation",
            integrity["invalid_time_conflict"],
            "TIME_CONFLICT payloads must overlap an already successful course for the same student.",
        )
        self._failure_samples(
            report_dir / "prerequisite_payload_validation_report.md",
            "PREREQUISITE_FAIL Payload Validation",
            integrity["invalid_prerequisite_fail"],
            "PREREQUISITE_FAIL payloads must be missing at least one required prerequisite course.",
        )
        self._failure_samples(
            report_dir / "scenario_label_consistency_report.md",
            "Scenario Label Consistency",
            integrity["scenario_label_inconsistencies"],
            "scenario_type and expected_status must agree with the success/failure contract.",
        )

    def _payload_integrity(self, path, metric):
        total = metric["total_actionable_failures"]
        self._write(path, [
            "# Payload Integrity Validation", "",
            f"Overall: **{'PASS' if total == 0 else 'FAIL'}**", "",
            "| Check | Failures |", "|---|---:|",
            f"| Scenario distribution mismatch count | {metric.get('scenario_distribution_mismatch_count', 0):,} |",
            f"| Expected status distribution mismatch count | {metric.get('expected_status_distribution_mismatch_count', 0):,} |",
            f"| Payload duplicate count | {metric['payload_duplicate_count']:,} |",
            f"| Invalid NORMAL count | {metric['invalid_normal_count']:,} |",
            f"| Invalid CAPACITY_OVER count | {metric['invalid_capacity_over_count']:,} |",
            f"| Invalid DUPLICATE count | {metric['invalid_duplicate_count']:,} |",
            f"| Invalid TIME_CONFLICT count | {metric['invalid_time_conflict_count']:,} |",
            f"| Invalid PREREQUISITE_FAIL count | {metric['invalid_prerequisite_fail_count']:,} |",
            f"| Scenario label inconsistency count | {metric['scenario_label_inconsistency_count']:,} |",
            f"| Total actionable failures | {total:,} |", "",
            "## Scenario distribution", "",
            "| scenario_type | Expected | Actual |", "|---|---:|---:|",
            *[
                f"| {scenario_type} | {expected:,} | {metric.get('scenario_distribution_actual', {}).get(scenario_type, 0):,} |"
                for scenario_type, expected in metric.get("scenario_distribution_expected", {}).items()
            ],
            "",
            "## Expected status distribution", "",
            "| expected_status | Expected | Actual |", "|---|---:|---:|",
            *[
                f"| {expected_status} | {expected:,} | {metric.get('expected_status_distribution_actual', {}).get(expected_status, 0):,} |"
                for expected_status, expected in metric.get("expected_status_distribution_expected", {}).items()
            ],
            "",
            "The payload is validated in scheduled execution order using `scheduled_offset_ms` and request_id as a stable tie-breaker.",
        ])

    def _duplicate_payload(self, path, metric):
        lines = [
            "# Duplicate Payload Validation", "",
            f"Result: **{'PASS' if metric['payload_duplicate_count'] == 0 else 'FAIL'}**", "",
            f"- Unexpected duplicate count in success-expected payloads: {metric['payload_duplicate_count']:,}",
            f"- Duplicate pairs shown below are the top {len(metric['duplicate_top'])} pairs across the full payload.", "",
            "## Full payload duplicate top N", "",
        ]
        lines.extend(self._duplicate_table(metric["duplicate_top"]))
        lines.extend(["", "## Success-expected duplicate top N", ""])
        lines.extend(self._duplicate_table(metric["unexpected_duplicate_top"]))
        self._write(path, lines)

    @staticmethod
    def _duplicate_table(rows):
        if not rows:
            return ["No duplicate pairs found."]
        lines = [
            "| student_id | course_id | count | duplicate_count | request_ids | scenario_counts |",
            "|---:|---:|---:|---:|---|---|",
        ]
        for row in rows:
            request_ids = ", ".join(str(value) for value in row["request_ids"])
            scenario_counts = ", ".join(f"{key}={value}" for key, value in sorted(row["scenario_counts"].items()))
            lines.append(f"| {row['student_id']} | {row['course_id']} | {row['count']} | {row['duplicate_count']} | {request_ids} | {scenario_counts} |")
        return lines

    def _failure_samples(self, path, title, rows, description, limit=100):
        lines = [
            f"# {title}", "",
            f"Result: **{'PASS' if not rows else 'FAIL'}**", "",
            description, "",
            f"- Failure count: {len(rows):,}", "",
        ]
        if rows:
            lines.extend([
                f"## Failure samples (top {min(limit, len(rows))})", "",
                "| request_id | student_id | course_id | scenario_type | expected_status | scheduled_offset_ms | reason |",
                "|---:|---:|---:|---|---:|---:|---|",
            ])
            for row in rows[:limit]:
                reason = str(row["reason"]).replace("|", "\\|")
                lines.append(
                    f"| {row['request_id']} | {row['student_id']} | {row['course_id']} | {row['scenario_type']} | "
                    f"{row['expected_status']} | {row['scheduled_offset_ms']} | {reason} |"
                )
        self._write(path, lines)

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
            "Baseline enrollment is intentionally empty. TIME_CONFLICT verification compares each targeted request with a prior NORMAL/HOTSPOT success request for the same student in scheduled execution order.", "",
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
        payload_integrity = context.metadata.get("payload_integrity", {})
        payload_actionable_failures = payload_integrity.get("total_actionable_failures", 0)
        validation_rule_failures = domain_failures + payload_failures + prerequisite_failures + schedule_failures
        lines = [
            "# Mock Data Harness Summary", "",
            f"Overall: **{'PASS' if validation_rule_failures == 0 else 'FAIL'}**", "",
            "## Generated scale", "",
            "| Dataset | Rows |", "|---|---:|",
            *[f"| `{name}` | {len(rows):,} |" for name, rows in context.data.items()], "",
            "## Validation results", "",
            f"- Domain validation failures: {domain_failures}",
            f"- Payload validation failures: {payload_failures}",
            f"- Invalid prerequisite scenarios: {prerequisite_failures}",
            f"- Invalid time-conflict scenarios: {schedule_failures}",
            f"- Credit validation: {analysis['credit']['status']}",
            f"- Validation rule failures: {validation_rule_failures}",
            f"- Total actionable failures: {payload_actionable_failures:,}", "",
            "## Payload integrity validation", "",
            f"- Payload duplicate count: {payload_integrity.get('payload_duplicate_count', 0):,}",
            f"- Scenario distribution mismatch count: {payload_integrity.get('scenario_distribution_mismatch_count', 0):,}",
            f"- Expected status distribution mismatch count: {payload_integrity.get('expected_status_distribution_mismatch_count', 0):,}",
            f"- Invalid NORMAL count: {payload_integrity.get('invalid_normal_count', 0):,}",
            f"- Invalid CAPACITY_OVER count: {payload_integrity.get('invalid_capacity_over_count', 0):,}",
            f"- Invalid DUPLICATE count: {payload_integrity.get('invalid_duplicate_count', 0):,}",
            f"- Invalid TIME_CONFLICT count: {payload_integrity.get('invalid_time_conflict_count', 0):,}",
            f"- Invalid PREREQUISITE_FAIL count: {payload_integrity.get('invalid_prerequisite_fail_count', 0):,}",
            f"- Scenario label inconsistency count: {payload_integrity.get('scenario_label_inconsistency_count', 0):,}",
            f"- Payload actionable failures: {payload_actionable_failures:,}", "",
            "### Payload scenario distribution", "",
            "| scenario_type | Expected | Actual |", "|---|---:|---:|",
            *[
                f"| {scenario_type} | {expected:,} | {payload_integrity.get('scenario_distribution_actual', {}).get(scenario_type, 0):,} |"
                for scenario_type, expected in payload_integrity.get("scenario_distribution_expected", {}).items()
            ],
            "",
            "### Payload expected_status distribution", "",
            "| expected_status | Expected | Actual |", "|---|---:|---:|",
            *[
                f"| {expected_status} | {expected:,} | {payload_integrity.get('expected_status_distribution_actual', {}).get(expected_status, 0):,} |"
                for expected_status, expected in payload_integrity.get("expected_status_distribution_expected", {}).items()
            ],
            "",
            "## Key distributions", "",
            f"- Hotspot courses: {analysis['hotspot']['hotspot_course_count']:,}/{analysis['hotspot']['course_total']:,} ({analysis['hotspot']['course_ratio']:.2%})",
            f"- Hotspot requests: {analysis['hotspot']['hotspot_request_count']:,}/{analysis['hotspot']['request_total']:,} ({analysis['hotspot']['request_ratio']:.2%})",
            f"- Prerequisite failure scenarios verified: {analysis['prerequisite']['correct_failure_cases']:,}",
            f"- Time-conflict scenarios verified: {analysis['schedule']['correct_conflict_cases']:,}", "",
            "## Reports", "",
            "- [Core validation](validation_report.md)",
            "- [Payload validation](payload_report.md)",
            "- [Payload integrity](payload_integrity_report.md)",
            "- [Duplicate payload](duplicate_payload_report.md)",
            "- [NORMAL payload validation](normal_payload_validation_report.md)",
            "- [CAPACITY_OVER validation](capacity_over_validation_report.md)",
            "- [DUPLICATE scenario validation](duplicate_scenario_validation_report.md)",
            "- [TIME_CONFLICT validation](time_conflict_validation_report.md)",
            "- [PREREQUISITE_FAIL validation](prerequisite_payload_validation_report.md)",
            "- [Scenario label consistency](scenario_label_consistency_report.md)",
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
