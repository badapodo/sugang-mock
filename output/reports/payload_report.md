# Payload Validation Report

Overall: **FAIL**

| Result | Rule | Detail |
|---|---|---|
| PASS | payload row count | actual=80000, expected=80000 |
| PASS | hotspot request ratio | actual=0.6000, target=0.6000 |
| PASS | scheduled offset distribution | 0-10s=0.6000, 10-30s=0.4000 |
| PASS | scenario type ratios | actual={'NORMAL': 64000, 'CAPACITY_OVER': 6400, 'DUPLICATE': 3200, 'PREREQUISITE_FAIL': 3200, 'TIME_CONFLICT': 3200, 'CREDIT_LIMIT': 0}, expected={'NORMAL': 64000, 'CAPACITY_OVER': 6400, 'DUPLICATE': 3200, 'PREREQUISITE_FAIL': 3200, 'TIME_CONFLICT': 3200, 'CREDIT_LIMIT': 0} |
| PASS | payload references | all student/course IDs exist |
| PASS | expected status mapping | all statuses match scenario type |
| PASS | active users | actual=16000, expected=16000 |
| FAIL | payload duplicate integrity | unexpected success duplicate pairs=232 |
| FAIL | normal payload semantics | invalid NORMAL/success payloads=32455 |
| FAIL | capacity_over semantics | invalid CAPACITY_OVER payloads=3947 |
| FAIL | duplicate scenario semantics | invalid DUPLICATE payloads=2406 |
| FAIL | time_conflict semantics | invalid TIME_CONFLICT payloads=2050 |
| PASS | prerequisite_fail semantics | invalid PREREQUISITE_FAIL payloads=0 |
| PASS | scenario label consistency | inconsistent labels=0 |
