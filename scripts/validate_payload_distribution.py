#!/usr/bin/env python3
import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


SCENARIOS = [
    "NORMAL",
    "HOTSPOT",
    "PREREQUISITE_FAIL",
    "TIME_CONFLICT",
    "CAPACITY_OVER",
    "DUPLICATE",
]


def read_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        rows = [
            {key.strip(): (value or "").strip() for key, value in row.items()}
            for row in reader
        ]
    return reader.fieldnames or [], rows


def main():
    parser = argparse.ArgumentParser(description="Validate enrollment payload scenario/status distribution.")
    parser.add_argument("--payload", default="output/csv/enrollment_payload.csv", help="Path to enrollment_payload.csv")
    parser.add_argument("--expected-total", type=int, default=80000)
    parser.add_argument("--expected-success", type=int, default=64000, help="NORMAL + HOTSPOT success request count")
    parser.add_argument("--expected-hotspot", type=int, default=48000, help="Hotspot request count by scenario_type=HOTSPOT plus hotspot failure scenarios")
    parser.add_argument("--expected-prerequisite-fail", type=int, default=3200)
    parser.add_argument("--expected-time-conflict", type=int, default=3200)
    parser.add_argument("--min-capacity-over", type=int, default=3200)
    parser.add_argument("--min-duplicate", type=int, default=3200)
    args = parser.parse_args()

    payload_path = Path(args.payload)
    fieldnames, rows = read_rows(payload_path)
    failures = []

    required_columns = {"student_id", "course_id", "scenario_type", "expected_status", "scheduled_offset_ms"}
    missing_columns = sorted(required_columns - {name.strip() for name in fieldnames})
    if missing_columns:
        failures.append(f"missing required columns: {missing_columns}")

    blank_scenarios = [index for index, row in enumerate(rows, 1) if not row.get("scenario_type")]
    blank_statuses = [index for index, row in enumerate(rows, 1) if not row.get("expected_status")]
    if blank_scenarios:
        failures.append(f"blank scenario_type rows: {blank_scenarios[:10]}")
    if blank_statuses:
        failures.append(f"blank expected_status rows: {blank_statuses[:10]}")

    scenario_counts = Counter(row.get("scenario_type", "") for row in rows)
    status_counts = Counter(row.get("expected_status", "") for row in rows)

    success_count = scenario_counts["NORMAL"] + scenario_counts["HOTSPOT"]
    hotspot_request_count = (
        scenario_counts["HOTSPOT"]
        + scenario_counts["CAPACITY_OVER"]
        + scenario_counts["DUPLICATE"]
        + scenario_counts["PREREQUISITE_FAIL"]
        + scenario_counts["TIME_CONFLICT"]
    )
    failure_4xx_count = sum(count for status, count in status_counts.items() if status.startswith("4"))

    if len(rows) != args.expected_total:
        failures.append(f"total rows mismatch: actual={len(rows)}, expected={args.expected_total}")
    if success_count != args.expected_success:
        failures.append(f"NORMAL/HOTSPOT success count mismatch: actual={success_count}, expected={args.expected_success}")
    if hotspot_request_count != args.expected_hotspot:
        failures.append(f"hotspot request count mismatch: actual={hotspot_request_count}, expected={args.expected_hotspot}")
    if scenario_counts["PREREQUISITE_FAIL"] != args.expected_prerequisite_fail:
        failures.append(f"PREREQUISITE_FAIL count mismatch: actual={scenario_counts['PREREQUISITE_FAIL']}, expected={args.expected_prerequisite_fail}")
    if scenario_counts["TIME_CONFLICT"] != args.expected_time_conflict:
        failures.append(f"TIME_CONFLICT count mismatch: actual={scenario_counts['TIME_CONFLICT']}, expected={args.expected_time_conflict}")
    if scenario_counts["CAPACITY_OVER"] < args.min_capacity_over:
        failures.append(f"CAPACITY_OVER count below minimum: actual={scenario_counts['CAPACITY_OVER']}, min={args.min_capacity_over}")
    if scenario_counts["DUPLICATE"] < args.min_duplicate:
        failures.append(f"DUPLICATE count below minimum: actual={scenario_counts['DUPLICATE']}, min={args.min_duplicate}")

    print("# Payload Scenario Distribution")
    print(f"- total rows: {len(rows):,}")
    for scenario in SCENARIOS:
        print(f"- {scenario}: {scenario_counts[scenario]:,}")

    print("")
    print("# Expected Status Distribution")
    print(f"- 200 count: {status_counts['200']:,}")
    print(f"- 400/409 count: {failure_4xx_count:,}")
    for status, count in sorted(status_counts.items()):
        if status not in {"200"} and not status.startswith("4"):
            print(f"- {status or '<blank>'} count: {count:,}")

    print("")
    print("# Design Targets")
    print(f"- NORMAL/HOTSPOT success: {success_count:,}/{args.expected_success:,}")
    print(f"- HOTSPOT included requests: {hotspot_request_count:,}/{args.expected_hotspot:,}")

    if failures:
        print("")
        print("# Result")
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("")
    print("# Result")
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
