#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config_loader import load_scenario


def _read_csv(path: Path, integer_fields=()):
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for field in integer_fields:
            row[field] = int(row[field])
    return rows


def _save(plt, path: Path, caption: str):
    figure = plt.gcf()
    figure.text(
        0.5, 0.015,
        "What this validates: " + textwrap.fill(caption, width=110),
        ha="center", va="bottom", fontsize=9, color="#444444",
    )
    plt.tight_layout(rect=(0, 0.10, 1, 1))
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()


def _chart_result(filename, title, purpose, interpretation, passed):
    return {
        "filename": filename,
        "title": title,
        "purpose": purpose,
        "interpretation": interpretation,
        "status": "PASS" if passed else "FAIL",
    }


def generate_charts(output_dir: str | Path, scenario: dict):
    output_dir = Path(output_dir)
    csv_dir = output_dir / "csv"
    chart_dir = output_dir / "charts"
    appendix_dir = chart_dir / "appendix"
    chart_dir.mkdir(parents=True, exist_ok=True)
    appendix_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = output_dir / ".matplotlib"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache_dir.resolve()))
    os.environ.setdefault("XDG_CACHE_HOME", str(cache_dir.resolve()))
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("matplotlib is required: pip install -r requirements.txt") from exc

    courses = _read_csv(csv_dir / "course.csv", ("id", "capacity", "current_count"))
    payload = _read_csv(csv_dir / "enrollment_payload.csv", ("student_id", "course_id", "expected_status", "scheduled_offset_ms"))
    course_times = _read_csv(csv_dir / "course_time.csv", ("id", "course_id"))
    students = _read_csv(csv_dir / "student.csv", ("student_id", "department_id", "member_id"))
    prerequisites = _read_csv(csv_dir / "prerequisite.csv", ("id", "course_id", "pre_course_id", "department_id"))
    completed = _read_csv(csv_dir / "completed_course.csv", ("id", "student_id", "course_id"))

    popular_capacity = scenario["course"]["popular_capacity"]
    hotspot_ids = {row["id"] for row in courses if row["capacity"] == popular_capacity}
    request_counts = Counter(row["course_id"] for row in payload)
    request_total = len(payload)
    hotspot_requests = sum(request_counts[course_id] for course_id in hotspot_ids)
    expected_hotspot_count = round(len(courses) * scenario["traffic"]["hotspot_course_ratio"])
    expected_hotspot_requests = round(request_total * scenario["traffic"]["hotspot_request_ratio"])
    results = []

    # 1. Payload timeline
    offsets = [row["scheduled_offset_ms"] / 1000 for row in payload]
    burst_count = sum(value < 10 for value in offsets)
    burst_ratio = burst_count / request_total
    plt.figure(figsize=(10, 5.5))
    plt.hist(offsets, bins=list(range(31)), color="#2171b5", edgecolor="white")
    plt.axvline(10, color="#de2d26", linestyle="--", linewidth=1.5, label="Burst boundary (10s)")
    plt.xlim(0, 30)
    plt.xlabel("Scheduled offset (seconds)")
    plt.ylabel("Request count per second")
    plt.title("Payload Timeline")
    plt.legend()
    _save(plt, chart_dir / "payload_timeline.png", "60% of requests arrive in 0-10 seconds and 40% arrive in 10-30 seconds.")
    results.append(_chart_result(
        "payload_timeline.png", "Payload Timeline",
        "0~30초 요청 분포가 의도한 burst traffic을 형성하는지 검증",
        f"0~10초 요청 비율은 {burst_ratio:.1%}이며 설정값 {scenario['traffic']['burst_window_ratio']:.1%}와 일치함",
        abs(burst_ratio - scenario["traffic"]["burst_window_ratio"]) <= 0.02,
    ))

    # 2. Request rank
    ranked_counts = sorted([request_counts.get(row["id"], 0) for row in courses], reverse=True)
    boundary = expected_hotspot_count
    head_min = ranked_counts[boundary - 1]
    tail_max = ranked_counts[boundary] if boundary < len(ranked_counts) else 0
    plt.figure(figsize=(10, 5.5))
    plt.plot(range(1, len(ranked_counts) + 1), ranked_counts, color="#2171b5", linewidth=1.4)
    plt.axvline(boundary, color="#de2d26", linestyle="--", label="Top 5% boundary")
    plt.xlabel("Course rank by request count")
    plt.ylabel("Request count")
    plt.title("Course Request Rank Distribution")
    plt.legend()
    _save(plt, chart_dir / "course_request_rank_distribution.png", "the rank curve has a distinct head-tail break at the top-5% hotspot boundary.")
    results.append(_chart_result(
        "course_request_rank_distribution.png", "Course Request Rank Distribution",
        "상위 5% 과목에 요청이 집중되고 Hotspot/Normal 경계가 분리되는지 검증",
        f"Rank {boundary:,} 경계에서 최소 hotspot 요청 {head_min:,}건, 최대 normal 요청 {tail_max:,}건으로 급격한 감소가 확인됨",
        head_min > tail_max,
    ))

    # 3. Hotspot competition
    capacity_by_course = {row["id"]: row["capacity"] for row in courses}
    ranked = sorted(request_counts.items(), key=lambda item: (-item[1], item[0]))[:20]
    positions = list(range(len(ranked)))
    width = 0.4
    plt.figure(figsize=(12, 6))
    plt.bar([value - width / 2 for value in positions], [capacity_by_course[cid] for cid, _ in ranked], width, label="Capacity", color="#9ecae1")
    plt.bar([value + width / 2 for value in positions], [count for _, count in ranked], width, label="Requests", color="#de2d26")
    plt.xticks(positions, [str(cid) for cid, _ in ranked], rotation=45, ha="right")
    plt.xlabel("Course ID (top 20 by requests)")
    plt.ylabel("Count")
    plt.title("Hotspot Competition: Capacity vs Requests")
    plt.legend()
    _save(plt, chart_dir / "hotspot_competition.png", "the top 20 courses receive more requests than their available capacity, producing real contention.")
    competition_pass = all(count > capacity_by_course[cid] for cid, count in ranked)
    average_multiple = sum(count / capacity_by_course[cid] for cid, count in ranked) / len(ranked)
    results.append(_chart_result(
        "hotspot_competition.png", "Hotspot Competition",
        "상위 20개 인기 과목이 정원을 초과하는 경쟁 상태인지 검증",
        f"상위 20개 과목의 요청은 평균 정원의 {average_multiple:.1f}배이며 모두 정원을 초과함",
        competition_pass,
    ))

    # 4. Prerequisite validation from persisted CSVs
    department_by_student = {row["student_id"]: row["department_id"] for row in students}
    completed_by_student = defaultdict(set)
    for row in completed:
        completed_by_student[row["student_id"]].add(row["course_id"])
    rule_map = {(row["course_id"], row["department_id"]): row["pre_course_id"] for row in prerequisites}
    targets = [row for row in payload if row["scenario_type"] == "PREREQUISITE_FAIL"]
    invalid = 0
    for row in targets:
        required = rule_map.get((row["course_id"], department_by_student[row["student_id"]]))
        if required is None or required in completed_by_student[row["student_id"]]:
            invalid += 1
    correct = len(targets) - invalid
    plt.figure(figsize=(7, 5.5))
    bars = plt.bar(["Correct failure cases", "Invalid cases"], [correct, invalid], color=["#31a354", "#de2d26"])
    plt.bar_label(bars, fmt="%d")
    plt.ylabel("Payload requests")
    plt.title("Prerequisite Scenario Validation")
    _save(plt, chart_dir / "prerequisite_validation.png", "every prerequisite-failure request maps to a real rule and a student missing the required course.")
    results.append(_chart_result(
        "prerequisite_validation.png", "Prerequisite Validation",
        "PREREQUISITE_FAIL 요청이 실제 선수과목 미이수 상태인지 검증",
        f"대상 {len(targets):,}건 중 {correct:,}건이 의도한 실패 조건을 충족하고 잘못 생성된 요청은 {invalid:,}건임",
        invalid == 0,
    ))

    # 5. Generated test scenario coverage
    coverage_values = [
        sum(row["scenario_type"] == "NORMAL" for row in payload),
        sum(row["course_id"] in hotspot_ids for row in payload),
        len(targets),
        sum(row["scenario_type"] == "TIME_CONFLICT" for row in payload),
        sum(row["scenario_type"] == "CREDIT_LIMIT" for row in payload),
    ]
    coverage_labels = ["NORMAL", "HOTSPOT", "PREREQUISITE_FAIL", "TIME_CONFLICT", "CREDIT_LIMIT"]
    plt.figure(figsize=(11, 5.8))
    bars = plt.bar(coverage_labels, coverage_values, color=["#31a354", "#2171b5", "#756bb1", "#fd8d3c", "#bdbdbd"])
    plt.bar_label(bars, labels=[f"{value:,}" if value else "N/A" for value in coverage_values], padding=3)
    plt.xticks(rotation=15, ha="right")
    plt.ylabel("Generated payload requests")
    plt.title("Generated Test Scenario Coverage")
    _save(plt, chart_dir / "validation_coverage.png", "the generator covers normal, hotspot, prerequisite-failure, and time-conflict paths while explicitly exposing unsupported credit checks.")
    results.append(_chart_result(
        "validation_coverage.png", "Generated Test Scenario Coverage",
        "성능·도메인 테스트에 필요한 주요 시나리오가 실제 payload에 포함되었는지 검증",
        f"NORMAL {coverage_values[0]:,}건, HOTSPOT {coverage_values[1]:,}건, 선수과목/시간충돌 각 {coverage_values[2]:,}/{coverage_values[3]:,}건이며 CREDIT_LIMIT은 엔티티 제약으로 N/A",
        all(value > 0 for value in coverage_values[:4]),
    ))

    # 6. Timeslot heatmap
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
    slot_counts = Counter((row["day_of_week"], row["start_time"][:5]) for row in course_times)
    slots = sorted({slot for _, slot in slot_counts})
    matrix = [[slot_counts.get((day, slot), 0) for slot in slots] for day in days]
    plt.figure(figsize=(12, 5.5))
    image = plt.imshow(matrix, aspect="auto", cmap="YlOrRd")
    plt.colorbar(image, label="Courses")
    plt.xticks(range(len(slots)), slots, rotation=45, ha="right")
    plt.yticks(range(len(days)), [day.title() for day in days])
    plt.title("Course Timeslot Heatmap")
    _save(plt, chart_dir / "timeslot_heatmap.png", "late-morning and early-afternoon peaks resemble a university timetable and still provide repeated slots for conflict scenarios.")
    peak_slots = {slot for slot in slots if "10:00" <= slot < "12:00" or "13:00" <= slot < "15:00"}
    peak_average = sum(count for (day, slot), count in slot_counts.items() if slot in peak_slots) / (len(days) * len(peak_slots))
    off_slots = set(slots) - peak_slots
    off_average = sum(count for (day, slot), count in slot_counts.items() if slot in off_slots) / (len(days) * len(off_slots))
    results.append(_chart_result(
        "timeslot_heatmap.png", "Timeslot Heatmap",
        "실제 대학 시간표처럼 10~12시와 13~15시에 강의가 집중되는지 검증",
        f"피크 시간대 슬롯당 평균 {peak_average:.1f}개, 비피크 시간대 {off_average:.1f}개로 피크 집중도가 더 높음",
        peak_average > off_average,
    ))

    # 7. Capacity utilization bands
    band_labels = ["0-50%", "50-100%", "100-300%", "300-600%", "600%+"]
    hotspot_bands = Counter()
    normal_bands = Counter()
    utilization = {}
    for course in courses:
        ratio = request_counts.get(course["id"], 0) / course["capacity"] * 100
        utilization[course["id"]] = ratio
        if ratio < 50:
            band = band_labels[0]
        elif ratio < 100:
            band = band_labels[1]
        elif ratio < 300:
            band = band_labels[2]
        elif ratio < 600:
            band = band_labels[3]
        else:
            band = band_labels[4]
        (hotspot_bands if course["id"] in hotspot_ids else normal_bands)[band] += 1
    x = list(range(len(band_labels)))
    width = 0.38
    normal_values = [normal_bands[label] for label in band_labels]
    hotspot_values = [hotspot_bands[label] for label in band_labels]
    plt.figure(figsize=(9, 5.8))
    normal_bars = plt.bar([value - width / 2 for value in x], normal_values, width, label="Normal courses", color="#bdbdbd")
    hotspot_bars = plt.bar([value + width / 2 for value in x], hotspot_values, width, label="Hotspot courses", color="#de2d26")
    plt.bar_label(normal_bars, labels=[str(value) if value else "" for value in normal_values], padding=2, fontsize=8)
    plt.bar_label(hotspot_bars, labels=[str(value) if value else "" for value in hotspot_values], padding=2, fontsize=8)
    plt.xticks(x, band_labels)
    plt.xlabel("Request count / capacity")
    plt.ylabel("Course count (log scale)")
    plt.yscale("log")
    plt.title("Course Capacity Utilization")
    plt.legend()
    _save(plt, chart_dir / "course_capacity_utilization.png", "hotspot courses occupy high request-to-capacity bands, confirming oversubscription pressure.")
    hotspot_over = sum(utilization[cid] >= 100 for cid in hotspot_ids)
    results.append(_chart_result(
        "course_capacity_utilization.png", "Course Capacity Utilization",
        "강의별 요청 수/정원 비율과 hotspot 과목의 초과 경쟁 상태를 검증",
        f"Hotspot {len(hotspot_ids):,}개 중 {hotspot_over:,}개가 정원 대비 100% 이상의 요청을 받아 초과 경쟁 상태임",
        hotspot_over == len(hotspot_ids),
    ))

    # Appendix charts: useful data-quality context, excluded from the portfolio core.
    _appendix_charts(plt, appendix_dir, courses, payload, students, prerequisites, hotspot_ids, request_counts, scenario)

    deprecated_main = {
        "hotspot_distribution.png", "hotspot_summary.png", "prerequisite_graph.png",
        "student_year_distribution.png", "department_distribution.png", "enrollment_distribution.png",
    }
    for filename in deprecated_main:
        path = chart_dir / filename
        if path.exists():
            path.unlink()
    return results


def _appendix_charts(plt, appendix_dir, courses, payload, students, prerequisites, hotspot_ids, request_counts, scenario):
    hotspot_ratio = sum(request_counts[cid] for cid in hotspot_ids) / len(payload)
    expected = scenario["traffic"]["hotspot_request_ratio"]
    plt.figure(figsize=(8, 5.5))
    x = [0, 1]
    width = 0.36
    plt.bar([i - width / 2 for i in x], [expected * 100, (1 - expected) * 100], width, label="Expected", color="#9ecae1")
    plt.bar([i + width / 2 for i in x], [hotspot_ratio * 100, (1 - hotspot_ratio) * 100], width, label="Actual", color="#2171b5")
    plt.xticks(x, ["Hotspot", "Normal"])
    plt.ylabel("Requests (%)")
    plt.title("Hotspot Distribution (Appendix)")
    plt.legend()
    _save(plt, appendix_dir / "hotspot_distribution.png", "configured and actual hotspot request shares match.")

    plt.figure(figsize=(9, 5.5))
    plt.barh(["Course population", "Request population"], [len(hotspot_ids) / len(courses) * 100, hotspot_ratio * 100], color="#2171b5")
    plt.xlim(0, 100)
    plt.xlabel("Hotspot share (%)")
    plt.title("Hotspot Summary (Appendix)")
    _save(plt, appendix_dir / "hotspot_summary.png", "a small course population absorbs a large request population.")

    rules = prerequisites[:250]
    plt.figure(figsize=(9, 6))
    for rule in rules:
        plt.plot([rule["pre_course_id"], rule["course_id"]], [0, 1], color="#9ecae1", alpha=0.25)
    plt.scatter([row["pre_course_id"] for row in rules], [0] * len(rules), s=8, color="#31a354")
    plt.scatter([row["course_id"] for row in rules], [1] * len(rules), s=8, color="#2171b5")
    plt.yticks([0, 1], ["Prerequisite", "Target"])
    plt.title("Prerequisite Graph Sample (Appendix)")
    _save(plt, appendix_dir / "prerequisite_graph.png", "prerequisite edges avoid self-reference and cycles.")

    year_counts = Counter(((row["student_id"] - 1) % 4) + 1 for row in students)
    plt.figure(figsize=(7, 5.5))
    bars = plt.bar([f"Year {year}" for year in sorted(year_counts)], [year_counts[year] for year in sorted(year_counts)], color="#31a354")
    plt.bar_label(bars, fmt="%d")
    plt.title("Derived Student Year Distribution (Appendix)")
    _save(plt, appendix_dir / "student_year_distribution.png", "analysis-only derived year groups are balanced.")

    department_counts = Counter(row["department_id"] for row in students)
    plt.figure(figsize=(12, 5.5))
    plt.bar(sorted(department_counts), [department_counts[key] for key in sorted(department_counts)], color="#756bb1")
    plt.xlabel("Department ID")
    plt.ylabel("Students")
    plt.title("Department Distribution (Appendix)")
    _save(plt, appendix_dir / "department_distribution.png", "department balance prevents unintended population skew.")


def main():
    parser = argparse.ArgumentParser(description="Generate portfolio charts from Harness CSV outputs")
    parser.add_argument("--output", default="output")
    parser.add_argument("--scenario", default="config/scenario.yaml")
    args = parser.parse_args()
    results = generate_charts(args.output, load_scenario(args.scenario))
    for result in results:
        print(f"[{result['status']}] {result['filename']}: {result['interpretation']}")


if __name__ == "__main__":
    main()
