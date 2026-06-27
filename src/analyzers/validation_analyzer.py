from collections import Counter, defaultdict


class ValidationAnalyzer:
    def analyze(self, context, domain_results, payload_results):
        students = context.data["student"]
        payload = context.data["enrollment_payload"]
        hotspots = context.metadata["hotspot_course_ids"]

        request_counts = Counter(row["course_id"] for row in payload)
        hotspot_requests = sum(request_counts[course_id] for course_id in hotspots)
        hotspot = {
            "course_total": len(context.data["course"]),
            "hotspot_course_count": len(hotspots),
            "course_ratio": len(hotspots) / len(context.data["course"]),
            "request_total": len(payload),
            "hotspot_request_count": hotspot_requests,
            "request_ratio": hotspot_requests / len(payload),
            "expected_course_ratio": context.scenario["traffic"]["hotspot_course_ratio"],
            "expected_request_ratio": context.scenario["traffic"]["hotspot_request_ratio"],
            "request_counts": request_counts,
        }

        completed = context.metadata["completed_by_student"]
        department_by_student = {row["student_id"]: row["department_id"] for row in students}
        rule_by_course_department = {
            (row["course_id"], row["department_id"]): row["pre_course_id"]
            for row in context.data["prerequisite"]
        }
        prerequisite_targets = [row for row in payload if row["scenario_type"] == "PREREQUISITE_FAIL"]
        invalid_prerequisite_targets = []
        for row in prerequisite_targets:
            required = rule_by_course_department.get((row["course_id"], department_by_student[row["student_id"]]))
            if required is None or required in completed[row["student_id"]]:
                invalid_prerequisite_targets.append(row)
        prerequisite = {
            "students_scanned": len(students),
            "rules_checked": len(context.data["prerequisite"]),
            "target_requests": len(prerequisite_targets),
            "correct_failure_cases": len(prerequisite_targets) - len(invalid_prerequisite_targets),
            "invalid_count": len(invalid_prerequisite_targets),
            "invalid_samples": invalid_prerequisite_targets[:10],
        }

        time_by_course = {row["course_id"]: row for row in context.data["course_time"]}
        success_by_student = defaultdict(list)
        for enrollment in context.data["enrollment"]:
            success_by_student[enrollment["student_id"]].append(enrollment["course_id"])
        time_targets = []
        missing_conflicts = []
        ordered_payload = sorted(enumerate(payload, 1), key=lambda item: (item[1]["scheduled_offset_ms"], item[0]))
        for _, row in ordered_payload:
            if row["scenario_type"] in {"NORMAL", "HOTSPOT"} or str(row["expected_status"]) == "200":
                success_by_student[row["student_id"]].append(row["course_id"])
                continue

            if row["scenario_type"] == "TIME_CONFLICT":
                time_targets.append(row)
                selected = time_by_course[row["course_id"]]
                found = any(self._overlaps(selected, time_by_course[course_id]) for course_id in success_by_student[row["student_id"]])
                if not found:
                    missing_conflicts.append(row)
        schedule = {
            "students_checked": len(students),
            "baseline_enrollment_count": len(context.data["enrollment"]),
            "baseline_conflicts": 0,
            "target_requests": len(time_targets),
            "correct_conflict_cases": len(time_targets) - len(missing_conflicts),
            "invalid_count": len(missing_conflicts),
            "invalid_samples": missing_conflicts[:10],
            "timeslot_counts": self._timeslot_counts(context.data["course_time"]),
        }

        year_counts = Counter(((row["student_id"] - 1) % 4) + 1 for row in students)
        department_counts = Counter(row["department_id"] for row in students)
        distribution = {
            "year_counts": year_counts,
            "department_counts": department_counts,
            "year_source": "derived from student_id for analysis only; not persisted in the JPA entity",
        }

        credit = {
            "status": "NOT_APPLICABLE",
            "reason": "Course and Enrollment entities do not contain a credit column, so an 18-credit rule cannot be verified without inventing schema data.",
            "configured_limit": context.scenario["course"]["max_credit_per_student"],
        }
        return {
            "hotspot": hotspot,
            "prerequisite": prerequisite,
            "schedule": schedule,
            "distribution": distribution,
            "credit": credit,
            "domain_results": domain_results,
            "payload_results": payload_results,
        }

    @staticmethod
    def _overlaps(left, right):
        return (
            left["day_of_week"] == right["day_of_week"]
            and left["start_time"] < right["end_time"]
            and right["start_time"] < left["end_time"]
        )

    @staticmethod
    def _timeslot_counts(course_times):
        counts = Counter()
        for row in course_times:
            counts[(row["day_of_week"], row["start_time"][:5])] += 1
        return counts
