# Payload Validation Report

Overall: **PASS**

| Result | Rule | Detail |
|---|---|---|
| PASS | payload row count | actual=80000, expected=80000 |
| PASS | hotspot request ratio | actual=0.6000, target=0.6000 |
| PASS | scheduled offset distribution | 0-10s=0.6000, 10-30s=0.4000 |
| PASS | scenario type ratios | actual={'NORMAL': 32000, 'HOTSPOT': 32000, 'CAPACITY_OVER': 6400, 'DUPLICATE': 3200, 'PREREQUISITE_FAIL': 3200, 'TIME_CONFLICT': 3200}, expected={'NORMAL': 32000, 'HOTSPOT': 32000, 'CAPACITY_OVER': 6400, 'DUPLICATE': 3200, 'PREREQUISITE_FAIL': 3200, 'TIME_CONFLICT': 3200} |
| PASS | payload references | all student/course IDs exist |
| PASS | expected status mapping | all statuses match scenario type |
| PASS | active users | actual=16000, expected=16000 |
| PASS | payload scenario distribution integrity | mismatches=0, actual={'NORMAL': 32000, 'HOTSPOT': 32000, 'CAPACITY_OVER': 6400, 'DUPLICATE': 3200, 'PREREQUISITE_FAIL': 3200, 'TIME_CONFLICT': 3200}, expected={'NORMAL': 32000, 'HOTSPOT': 32000, 'CAPACITY_OVER': 6400, 'DUPLICATE': 3200, 'PREREQUISITE_FAIL': 3200, 'TIME_CONFLICT': 3200} |
| PASS | payload expected_status distribution integrity | mismatches=0, actual={'200': 64000, '400': 16000}, expected={'200': 64000, '400': 16000} |
| PASS | payload duplicate integrity | unexpected success duplicate pairs=0 |
| PASS | normal payload semantics | invalid NORMAL/success payloads=0 |
| PASS | capacity_over semantics | invalid CAPACITY_OVER payloads=0 |
| PASS | duplicate scenario semantics | invalid DUPLICATE payloads=0 |
| PASS | time_conflict semantics | invalid TIME_CONFLICT payloads=0 |
| PASS | prerequisite_fail semantics | invalid PREREQUISITE_FAIL payloads=0 |
| PASS | scenario label consistency | inconsistent labels=0 |
