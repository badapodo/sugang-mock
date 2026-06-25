# Payload Integrity Validation

Overall: **PASS**

| Check | Failures |
|---|---:|
| Payload duplicate count | 0 |
| Invalid NORMAL count | 0 |
| Invalid CAPACITY_OVER count | 0 |
| Invalid DUPLICATE count | 0 |
| Invalid TIME_CONFLICT count | 0 |
| Invalid PREREQUISITE_FAIL count | 0 |
| Scenario label inconsistency count | 0 |
| Total actionable failures | 0 |

The payload is validated in scheduled execution order using `scheduled_offset_ms` and request_id as a stable tie-breaker.
