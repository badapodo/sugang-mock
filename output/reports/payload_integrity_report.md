# Payload Integrity Validation

Overall: **FAIL**

| Check | Failures |
|---|---:|
| Payload duplicate count | 232 |
| Invalid NORMAL count | 32,455 |
| Invalid CAPACITY_OVER count | 3,947 |
| Invalid DUPLICATE count | 2,406 |
| Invalid TIME_CONFLICT count | 2,050 |
| Invalid PREREQUISITE_FAIL count | 0 |
| Scenario label inconsistency count | 0 |
| Total actionable failures | 41,090 |

The payload is validated in scheduled execution order using `scheduled_offset_ms` and request_id as a stable tie-breaker.
