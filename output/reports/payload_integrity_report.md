# Payload Integrity Validation

Overall: **PASS**

| Check | Failures |
|---|---:|
| Scenario distribution mismatch count | 0 |
| Expected status distribution mismatch count | 0 |
| Payload duplicate count | 0 |
| Invalid NORMAL count | 0 |
| Invalid CAPACITY_OVER count | 0 |
| Invalid DUPLICATE count | 0 |
| Invalid TIME_CONFLICT count | 0 |
| Invalid PREREQUISITE_FAIL count | 0 |
| Scenario label inconsistency count | 0 |
| Total actionable failures | 0 |

## Scenario distribution

| scenario_type | Expected | Actual |
|---|---:|---:|
| NORMAL | 32,000 | 32,000 |
| HOTSPOT | 32,000 | 32,000 |
| CAPACITY_OVER | 6,400 | 6,400 |
| DUPLICATE | 3,200 | 3,200 |
| PREREQUISITE_FAIL | 3,200 | 3,200 |
| TIME_CONFLICT | 3,200 | 3,200 |

## Expected status distribution

| expected_status | Expected | Actual |
|---|---:|---:|
| 200 | 64,000 | 64,000 |
| 400 | 16,000 | 16,000 |

The payload is validated in scheduled execution order using `scheduled_offset_ms` and request_id as a stable tie-breaker.
