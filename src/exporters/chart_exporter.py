from __future__ import annotations

import os


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
        self._hotspot(plt, chart_dir, analysis["hotspot"])
        self._enrollment(plt, chart_dir, context, analysis["hotspot"])
        self._student_year(plt, chart_dir, analysis["distribution"])
        self._department(plt, chart_dir, analysis["distribution"])
        self._timeslot(plt, chart_dir, analysis["schedule"])
        self._prerequisite_validation(plt, chart_dir, analysis["prerequisite"])
        self._prerequisite_graph(plt, chart_dir, context)

    @staticmethod
    def _save(plt, path):
        plt.tight_layout()
        plt.savefig(path, dpi=160, bbox_inches="tight")
        plt.close()

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
        self._save(plt, chart_dir / "hotspot_distribution.png")

    def _enrollment(self, plt, chart_dir, context, metric):
        counts = [metric["request_counts"].get(row["id"], 0) for row in context.data["course"]]
        plt.figure(figsize=(9, 5))
        plt.hist(counts, bins=30, color="#3182bd", edgecolor="white")
        plt.xlabel("Requests per course")
        plt.ylabel("Course count")
        plt.title("Enrollment Request Distribution")
        self._save(plt, chart_dir / "enrollment_distribution.png")

    def _student_year(self, plt, chart_dir, distribution):
        years = sorted(distribution["year_counts"])
        values = [distribution["year_counts"][year] for year in years]
        plt.figure(figsize=(7, 5))
        bars = plt.bar([f"Year {year}" for year in years], values, color="#31a354")
        plt.bar_label(bars, fmt="%d")
        plt.ylabel("Students")
        plt.title("Student Distribution by Derived Year")
        self._save(plt, chart_dir / "student_year_distribution.png")

    def _department(self, plt, chart_dir, distribution):
        departments = sorted(distribution["department_counts"])
        values = [distribution["department_counts"][department] for department in departments]
        plt.figure(figsize=(12, 5))
        plt.bar(departments, values, color="#756bb1", width=0.85)
        plt.xlabel("Department ID")
        plt.ylabel("Students")
        plt.title("Student Distribution by Department")
        self._save(plt, chart_dir / "department_distribution.png")

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
        self._save(plt, chart_dir / "timeslot_heatmap.png")

    def _prerequisite_validation(self, plt, chart_dir, prerequisite):
        correct = prerequisite["correct_failure_cases"]
        invalid = prerequisite["invalid_count"]
        plt.figure(figsize=(7, 5))
        bars = plt.bar(["Correct failure cases", "Invalid cases"], [correct, invalid], color=["#31a354", "#de2d26"])
        plt.bar_label(bars, fmt="%d")
        plt.ylabel("Payload requests")
        plt.title("Prerequisite Scenario Validation")
        self._save(plt, chart_dir / "prerequisite_validation.png")

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
        self._save(plt, chart_dir / "prerequisite_graph.png")
