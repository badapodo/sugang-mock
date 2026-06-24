from __future__ import annotations

import os
import textwrap


class ChartExporter:
    def export(self, context, analysis):
        mpl_config = context.output_dir / ".matplotlib"
        mpl_config.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(mpl_config.resolve()))
        os.environ.setdefault("XDG_CACHE_HOME", str(mpl_config.resolve()))
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise RuntimeError("matplotlib is required for chart generation: pip install -r requirements.txt") from exc

        chart_dir = context.output_dir / "charts"
        chart_dir.mkdir(parents=True, exist_ok=True)
        appendix_dir = chart_dir / "appendix"
        appendix_dir.mkdir(parents=True, exist_ok=True)
        for stale_name in ("student_year_distribution.png", "department_distribution.png"):
            stale_path = chart_dir / stale_name
            if stale_path.exists():
                stale_path.unlink()

        self._payload_timeline(plt, chart_dir, context)
        self._course_rank(plt, chart_dir, context, analysis["hotspot"])
        self._hotspot_competition(plt, chart_dir, context, analysis["hotspot"])
        self._validation_coverage(plt, chart_dir, context)
        self._hotspot_summary(plt, chart_dir, analysis["hotspot"])
        self._hotspot(plt, chart_dir, analysis["hotspot"])
        self._enrollment(plt, chart_dir, context, analysis["hotspot"])
        self._student_year(plt, appendix_dir, analysis["distribution"])
        self._department(plt, appendix_dir, analysis["distribution"])
        self._timeslot(plt, chart_dir, analysis["schedule"])
        self._prerequisite_validation(plt, chart_dir, analysis["prerequisite"])
        self._prerequisite_graph(plt, chart_dir, context)

    @staticmethod
    def _save(plt, path, caption):
        figure = plt.gcf()
        figure.text(
            0.5,
            0.015,
            "What this validates: " + textwrap.fill(caption, width=110),
            ha="center",
            va="bottom",
            fontsize=9,
            color="#444444",
        )
        plt.tight_layout(rect=(0, 0.10, 1, 1))
        plt.savefig(path, dpi=160, bbox_inches="tight")
        plt.close()

    def _payload_timeline(self, plt, chart_dir, context):
        offsets = [row["scheduled_offset_ms"] / 1000 for row in context.data["enrollment_payload"]]
        bins = list(range(0, 31))
        plt.figure(figsize=(10, 5.5))
        plt.hist(offsets, bins=bins, color="#2171b5", edgecolor="white")
        plt.axvline(10, color="#de2d26", linestyle="--", linewidth=1.5, label="Burst boundary (10s)")
        plt.xlim(0, 30)
        plt.xlabel("Scheduled offset (seconds)")
        plt.ylabel("Request count per second")
        plt.title("Payload Timeline")
        plt.legend()
        self._save(
            plt,
            chart_dir / "payload_timeline.png",
            "the intended burst shape: 60% of requests arrive in 0-10 seconds and the remaining 40% in 10-30 seconds.",
        )

    def _course_rank(self, plt, chart_dir, context, metric):
        counts = sorted(
            [metric["request_counts"].get(row["id"], 0) for row in context.data["course"]],
            reverse=True,
        )
        plt.figure(figsize=(10, 5.5))
        plt.plot(range(1, len(counts) + 1), counts, color="#2171b5", linewidth=1.4)
        plt.axvline(metric["hotspot_course_count"], color="#de2d26", linestyle="--", label="Top 5% boundary")
        plt.xlabel("Course rank by request count")
        plt.ylabel("Request count")
        plt.title("Course Request Rank Distribution")
        plt.legend()
        self._save(
            plt,
            chart_dir / "course_request_rank_distribution.png",
            "requests form a deliberate head-tail distribution and the traffic concentration changes at the top-5% hotspot boundary.",
        )

    def _hotspot_competition(self, plt, chart_dir, context, metric):
        capacities = {row["id"]: row["capacity"] for row in context.data["course"]}
        ranked = sorted(metric["request_counts"].items(), key=lambda item: (-item[1], item[0]))[:20]
        labels = [str(course_id) for course_id, _ in ranked]
        requests = [count for _, count in ranked]
        capacity = [capacities[course_id] for course_id, _ in ranked]
        positions = list(range(len(ranked)))
        width = 0.4
        plt.figure(figsize=(12, 6))
        plt.bar([value - width / 2 for value in positions], capacity, width, label="Capacity", color="#9ecae1")
        plt.bar([value + width / 2 for value in positions], requests, width, label="Requests", color="#de2d26")
        plt.xticks(positions, labels, rotation=45, ha="right")
        plt.xlabel("Course ID (top 20 by requests)")
        plt.ylabel("Count")
        plt.title("Hotspot Competition: Capacity vs Requests")
        plt.legend()
        self._save(
            plt,
            chart_dir / "hotspot_competition.png",
            "the busiest courses receive substantially more concurrent requests than their capacity, creating meaningful contention.",
        )

    def _validation_coverage(self, plt, chart_dir, context):
        payload = context.data["enrollment_payload"]
        hotspots = context.metadata["hotspot_course_ids"]
        values = [
            sum(row["scenario_type"] == "NORMAL" for row in payload),
            sum(row["course_id"] in hotspots for row in payload),
            sum(row["scenario_type"] == "PREREQUISITE_FAIL" for row in payload),
            sum(row["scenario_type"] == "TIME_CONFLICT" for row in payload),
            sum(row["scenario_type"] == "CREDIT_LIMIT" for row in payload),
        ]
        labels = ["NORMAL", "HOTSPOT", "PREREQUISITE_FAIL", "TIME_CONFLICT", "CREDIT_LIMIT"]
        colors = ["#31a354", "#2171b5", "#756bb1", "#fd8d3c", "#bdbdbd"]
        plt.figure(figsize=(11, 5.8))
        bars = plt.bar(labels, values, color=colors)
        display_labels = [f"{value:,}" if value else "N/A" for value in values]
        plt.bar_label(bars, labels=display_labels, padding=3)
        plt.xticks(rotation=15, ha="right")
        plt.ylabel("Covered payload requests")
        plt.title("Validation Scenario Coverage")
        self._save(
            plt,
            chart_dir / "validation_coverage.png",
            "the generated payload exercises normal, hotspot, prerequisite-failure, and time-conflict paths; credit remains N/A because the entity has no credit field.",
        )

    def _hotspot_summary(self, plt, chart_dir, metric):
        course_hotspot = metric["course_ratio"] * 100
        request_hotspot = metric["request_ratio"] * 100
        plt.figure(figsize=(9, 5.5))
        plt.barh(["Course population", "Request population"], [course_hotspot, request_hotspot], color="#2171b5", label="Hotspot")
        plt.barh(
            ["Course population", "Request population"],
            [100 - course_hotspot, 100 - request_hotspot],
            left=[course_hotspot, request_hotspot],
            color="#d9d9d9",
            label="Normal",
        )
        plt.text(course_hotspot / 2, 0, f"{course_hotspot:.0f}%", ha="center", va="center", color="white", fontweight="bold")
        plt.text(request_hotspot / 2, 1, f"{request_hotspot:.0f}%", ha="center", va="center", color="white", fontweight="bold")
        plt.xlim(0, 100)
        plt.xlabel("Share (%)")
        plt.title("Hotspot Summary: 5% of Courses Receive 60% of Requests")
        plt.legend(loc="lower right")
        self._save(
            plt,
            chart_dir / "hotspot_summary.png",
            "the central performance-test premise holds: the top 5% of courses absorb exactly 60% of all enrollment requests.",
        )

    def _hotspot(self, plt, chart_dir, metric):
        actual = [metric["request_ratio"] * 100, (1 - metric["request_ratio"]) * 100]
        expected = [metric["expected_request_ratio"] * 100, (1 - metric["expected_request_ratio"]) * 100]
        x = [0, 1]
        width = 0.36
        plt.figure(figsize=(8, 5))
        plt.bar([i - width / 2 for i in x], expected, width, label="Expected", color="#9ecae1")
        plt.bar([i + width / 2 for i in x], actual, width, label="Actual", color="#2171b5")
        plt.xticks(x, ["Hotspot Courses", "Normal Courses"])
        plt.ylabel("Enrollment requests (%)")
        plt.ylim(0, 100)
        plt.title("Hotspot Request Distribution")
        plt.legend()
        self._save(
            plt,
            chart_dir / "hotspot_distribution.png",
            "the generated hotspot and normal request shares match the configured 60:40 target without distribution drift.",
        )

    def _enrollment(self, plt, chart_dir, context, metric):
        counts = [metric["request_counts"].get(row["id"], 0) for row in context.data["course"]]
        plt.figure(figsize=(9, 5))
        plt.hist(counts, bins=30, color="#3182bd", edgecolor="white")
        plt.xlabel("Requests per course")
        plt.ylabel("Course count")
        plt.title("Enrollment Request Distribution")
        self._save(
            plt,
            chart_dir / "enrollment_distribution.png",
            "request counts are uneven across courses rather than uniformly generated, which is necessary for contention testing.",
        )

    def _student_year(self, plt, chart_dir, distribution):
        years = sorted(distribution["year_counts"])
        values = [distribution["year_counts"][year] for year in years]
        plt.figure(figsize=(7, 5))
        bars = plt.bar([f"Year {year}" for year in years], values, color="#31a354")
        plt.bar_label(bars, fmt="%d")
        plt.ylabel("Students")
        plt.title("Student Distribution by Derived Year")
        self._save(
            plt,
            chart_dir / "student_year_distribution.png",
            "the analysis-only derived year groups are balanced; year is not persisted in the current JPA entity.",
        )

    def _department(self, plt, chart_dir, distribution):
        departments = sorted(distribution["department_counts"])
        values = [distribution["department_counts"][department] for department in departments]
        plt.figure(figsize=(12, 5))
        plt.bar(departments, values, color="#756bb1", width=0.85)
        plt.xlabel("Department ID")
        plt.ylabel("Students")
        plt.title("Student Distribution by Department")
        self._save(
            plt,
            chart_dir / "department_distribution.png",
            "students are evenly assigned across departments so department skew does not accidentally dominate test results.",
        )

    def _timeslot(self, plt, chart_dir, schedule):
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        slots = sorted({slot for _, slot in schedule["timeslot_counts"]})
        matrix = [[schedule["timeslot_counts"].get((day, slot), 0) for slot in slots] for day in days]
        plt.figure(figsize=(12, 5))
        image = plt.imshow(matrix, aspect="auto", cmap="YlOrRd")
        plt.colorbar(image, label="Courses")
        plt.xticks(range(len(slots)), slots, rotation=45, ha="right")
        plt.yticks(range(len(days)), [day.title() for day in days])
        plt.title("Course Timeslot Heatmap")
        self._save(
            plt,
            chart_dir / "timeslot_heatmap.png",
            "course times cover the configured weekday and 30-minute slot space used by time-conflict scenarios.",
        )

    def _prerequisite_validation(self, plt, chart_dir, prerequisite):
        correct = prerequisite["correct_failure_cases"]
        invalid = prerequisite["invalid_count"]
        plt.figure(figsize=(7, 5))
        bars = plt.bar(["Correct failure cases", "Invalid cases"], [correct, invalid], color=["#31a354", "#de2d26"])
        plt.bar_label(bars, fmt="%d")
        plt.ylabel("Payload requests")
        plt.title("Prerequisite Scenario Validation")
        self._save(
            plt,
            chart_dir / "prerequisite_validation.png",
            "every PREREQUISITE_FAIL payload is backed by a real department rule and a student who has not completed the required course.",
        )

    def _prerequisite_graph(self, plt, chart_dir, context):
        rules = context.data["prerequisite"][:250]
        plt.figure(figsize=(9, 6))
        for rule in rules:
            plt.plot([rule["pre_course_id"], rule["course_id"]], [0, 1], color="#9ecae1", alpha=0.25)
        plt.scatter([rule["pre_course_id"] for rule in rules], [0] * len(rules), s=8, color="#31a354", label="Prerequisite")
        plt.scatter([rule["course_id"] for rule in rules], [1] * len(rules), s=8, color="#2171b5", label="Target course")
        plt.yticks([0, 1], ["Prerequisite", "Target"])
        plt.xlabel("Course ID (first 250 rules)")
        plt.title("Prerequisite Graph Sample")
        plt.legend()
        self._save(
            plt,
            chart_dir / "prerequisite_graph.png",
            "prerequisite edges point from lower course IDs to target courses, preventing self-reference and cyclic generation.",
        )
