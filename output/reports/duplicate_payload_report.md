# Duplicate Payload Validation

Result: **FAIL**

- Unexpected duplicate count in success-expected payloads: 232
- Duplicate pairs shown below are the top 20 pairs across the full payload.

## Full payload duplicate top N

| student_id | course_id | count | duplicate_count | request_ids | scenario_counts |
|---:|---:|---:|---:|---|---|
| 16776 | 2102 | 7 | 6 | 1459, 1557, 3551, 6937, 11193, 11258, 15377 | DUPLICATE=6, NORMAL=1 |
| 26694 | 2529 | 5 | 4 | 9, 71, 203, 874, 1796 | DUPLICATE=4, NORMAL=1 |
| 37727 | 134 | 5 | 4 | 3550, 9674, 12240, 29578, 33695 | DUPLICATE=4, NORMAL=1 |
| 2469 | 93 | 4 | 3 | 3883, 5353, 8934, 59981 | DUPLICATE=3, NORMAL=1 |
| 2478 | 3539 | 4 | 3 | 2419, 16566, 21496, 30841 | DUPLICATE=3, NORMAL=1 |
| 5353 | 539 | 4 | 3 | 16862, 39266, 44232, 51490 | DUPLICATE=3, NORMAL=1 |
| 6424 | 437 | 4 | 3 | 5967, 14445, 32994, 70069 | DUPLICATE=3, NORMAL=1 |
| 8665 | 121 | 4 | 3 | 3456, 25036, 25523, 30037 | DUPLICATE=1, PREREQUISITE_FAIL=3 |
| 8675 | 53 | 4 | 3 | 303, 1596, 3980, 4203 | DUPLICATE=3, NORMAL=1 |
| 9547 | 128 | 4 | 3 | 1192, 8256, 9076, 11632 | DUPLICATE=3, NORMAL=1 |
| 9663 | 195 | 4 | 3 | 28127, 30584, 50375, 66087 | DUPLICATE=3, NORMAL=1 |
| 10246 | 108 | 4 | 3 | 45, 74, 179, 39945 | DUPLICATE=3, NORMAL=1 |
| 13164 | 965 | 4 | 3 | 9811, 9962, 17655, 19819 | CAPACITY_OVER=1, DUPLICATE=3 |
| 15575 | 190 | 4 | 3 | 3363, 7196, 48304, 61517 | DUPLICATE=2, NORMAL=2 |
| 16236 | 4 | 4 | 3 | 25335, 32819, 34424, 77409 | DUPLICATE=3, NORMAL=1 |
| 17299 | 91 | 4 | 3 | 3655, 13157, 15311, 29628 | DUPLICATE=1, PREREQUISITE_FAIL=3 |
| 17941 | 101 | 4 | 3 | 2988, 7755, 21863, 71016 | DUPLICATE=2, PREREQUISITE_FAIL=2 |
| 17981 | 58 | 4 | 3 | 1835, 3027, 10996, 15798 | DUPLICATE=3, NORMAL=1 |
| 18926 | 129 | 4 | 3 | 2163, 12131, 25739, 70507 | DUPLICATE=3, NORMAL=1 |
| 19300 | 96 | 4 | 3 | 19, 32781, 55967, 59688 | DUPLICATE=1, PREREQUISITE_FAIL=3 |

## Success-expected duplicate top N

| student_id | course_id | count | duplicate_count | request_ids | scenario_counts |
|---:|---:|---:|---:|---|---|
| 39482 | 137 | 3 | 2 | 9781, 50801, 62895 | NORMAL=3 |
| 79 | 190 | 2 | 1 | 48682, 71667 | NORMAL=2 |
| 357 | 73 | 2 | 1 | 43960, 73334 | NORMAL=2 |
| 690 | 20 | 2 | 1 | 45139, 54555 | NORMAL=2 |
| 690 | 67 | 2 | 1 | 36820, 54817 | NORMAL=2 |
| 779 | 113 | 2 | 1 | 70651, 71336 | NORMAL=2 |
| 902 | 107 | 2 | 1 | 49876, 65570 | NORMAL=2 |
| 981 | 104 | 2 | 1 | 23496, 78103 | NORMAL=2 |
| 1089 | 197 | 2 | 1 | 6164, 15103 | NORMAL=2 |
| 1169 | 65 | 2 | 1 | 12572, 37608 | NORMAL=2 |
| 1461 | 103 | 2 | 1 | 10949, 20113 | NORMAL=2 |
| 1697 | 163 | 2 | 1 | 38757, 68108 | NORMAL=2 |
| 1812 | 144 | 2 | 1 | 7163, 55319 | NORMAL=2 |
| 1857 | 13 | 2 | 1 | 54680, 66100 | NORMAL=2 |
| 2090 | 18 | 2 | 1 | 39159, 44312 | NORMAL=2 |
| 2219 | 42 | 2 | 1 | 8126, 13536 | NORMAL=2 |
| 2243 | 158 | 2 | 1 | 6303, 38863 | NORMAL=2 |
| 2341 | 108 | 2 | 1 | 48926, 69264 | NORMAL=2 |
| 2550 | 28 | 2 | 1 | 49366, 70183 | NORMAL=2 |
| 3112 | 114 | 2 | 1 | 10645, 25407 | NORMAL=2 |
