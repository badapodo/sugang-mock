# DUPLICATE Scenario Validation

Result: **FAIL**

DUPLICATE payloads must have a prior successful request with the same student_id/course_id pair.

- Failure count: 2,406

## Failure samples (top 100)

| request_id | student_id | course_id | scenario_type | expected_status | scheduled_offset_ms | reason |
|---:|---:|---:|---|---:|---:|---|
| 60715 | 33758 | 96 | DUPLICATE | 400 | 2 | no prior successful request for same student_id/course_id |
| 593 | 3807 | 578 | DUPLICATE | 400 | 4 | no prior successful request for same student_id/course_id |
| 79771 | 38292 | 27 | DUPLICATE | 400 | 10 | no prior successful request for same student_id/course_id |
| 55691 | 35152 | 2831 | DUPLICATE | 400 | 20 | no prior successful request for same student_id/course_id |
| 11575 | 36916 | 179 | DUPLICATE | 400 | 21 | no prior successful request for same student_id/course_id |
| 18341 | 38920 | 50 | DUPLICATE | 400 | 31 | no prior successful request for same student_id/course_id |
| 53912 | 34130 | 1498 | DUPLICATE | 400 | 39 | no prior successful request for same student_id/course_id |
| 54920 | 4195 | 402 | DUPLICATE | 400 | 39 | no prior successful request for same student_id/course_id |
| 76627 | 5356 | 3878 | DUPLICATE | 400 | 42 | no prior successful request for same student_id/course_id |
| 48197 | 38528 | 155 | DUPLICATE | 400 | 44 | no prior successful request for same student_id/course_id |
| 38944 | 8807 | 1065 | DUPLICATE | 400 | 45 | no prior successful request for same student_id/course_id |
| 38921 | 37708 | 3518 | DUPLICATE | 400 | 50 | no prior successful request for same student_id/course_id |
| 6713 | 26794 | 95 | DUPLICATE | 400 | 51 | no prior successful request for same student_id/course_id |
| 8012 | 24107 | 131 | DUPLICATE | 400 | 56 | no prior successful request for same student_id/course_id |
| 21522 | 13044 | 2776 | DUPLICATE | 400 | 62 | no prior successful request for same student_id/course_id |
| 20985 | 35592 | 178 | DUPLICATE | 400 | 76 | no prior successful request for same student_id/course_id |
| 71988 | 1151 | 151 | DUPLICATE | 400 | 84 | no prior successful request for same student_id/course_id |
| 28273 | 25620 | 178 | DUPLICATE | 400 | 90 | no prior successful request for same student_id/course_id |
| 64283 | 31057 | 1077 | DUPLICATE | 400 | 98 | no prior successful request for same student_id/course_id |
| 11633 | 21364 | 2217 | DUPLICATE | 400 | 99 | no prior successful request for same student_id/course_id |
| 54820 | 24047 | 917 | DUPLICATE | 400 | 114 | no prior successful request for same student_id/course_id |
| 23640 | 39481 | 169 | DUPLICATE | 400 | 116 | no prior successful request for same student_id/course_id |
| 22012 | 18756 | 62 | DUPLICATE | 400 | 127 | no prior successful request for same student_id/course_id |
| 75769 | 30045 | 14 | DUPLICATE | 400 | 128 | no prior successful request for same student_id/course_id |
| 1557 | 16776 | 2102 | DUPLICATE | 400 | 130 | no prior successful request for same student_id/course_id |
| 57177 | 23579 | 3901 | DUPLICATE | 400 | 132 | no prior successful request for same student_id/course_id |
| 63066 | 751 | 65 | DUPLICATE | 400 | 132 | no prior successful request for same student_id/course_id |
| 49530 | 6934 | 37 | DUPLICATE | 400 | 136 | no prior successful request for same student_id/course_id |
| 881 | 12809 | 562 | DUPLICATE | 400 | 141 | no prior successful request for same student_id/course_id |
| 34798 | 10712 | 137 | DUPLICATE | 400 | 151 | no prior successful request for same student_id/course_id |
| 44953 | 7092 | 1179 | DUPLICATE | 400 | 151 | no prior successful request for same student_id/course_id |
| 63117 | 22547 | 1073 | DUPLICATE | 400 | 153 | no prior successful request for same student_id/course_id |
| 30404 | 31943 | 160 | DUPLICATE | 400 | 156 | no prior successful request for same student_id/course_id |
| 59132 | 22030 | 119 | DUPLICATE | 400 | 165 | no prior successful request for same student_id/course_id |
| 79759 | 25221 | 2844 | DUPLICATE | 400 | 166 | no prior successful request for same student_id/course_id |
| 16850 | 19887 | 174 | DUPLICATE | 400 | 168 | no prior successful request for same student_id/course_id |
| 24293 | 22941 | 2588 | DUPLICATE | 400 | 175 | no prior successful request for same student_id/course_id |
| 21231 | 8843 | 69 | DUPLICATE | 400 | 190 | no prior successful request for same student_id/course_id |
| 14582 | 36310 | 127 | DUPLICATE | 400 | 194 | no prior successful request for same student_id/course_id |
| 58672 | 29278 | 3356 | DUPLICATE | 400 | 198 | no prior successful request for same student_id/course_id |
| 10148 | 26147 | 26 | DUPLICATE | 400 | 213 | no prior successful request for same student_id/course_id |
| 44558 | 22225 | 408 | DUPLICATE | 400 | 215 | no prior successful request for same student_id/course_id |
| 68210 | 72 | 58 | DUPLICATE | 400 | 215 | no prior successful request for same student_id/course_id |
| 62845 | 34120 | 54 | DUPLICATE | 400 | 218 | no prior successful request for same student_id/course_id |
| 41348 | 10816 | 99 | DUPLICATE | 400 | 224 | no prior successful request for same student_id/course_id |
| 23776 | 15490 | 164 | DUPLICATE | 400 | 227 | no prior successful request for same student_id/course_id |
| 38150 | 37701 | 195 | DUPLICATE | 400 | 228 | no prior successful request for same student_id/course_id |
| 68353 | 29727 | 353 | DUPLICATE | 400 | 234 | no prior successful request for same student_id/course_id |
| 73662 | 19959 | 1654 | DUPLICATE | 400 | 241 | no prior successful request for same student_id/course_id |
| 72791 | 36954 | 1966 | DUPLICATE | 400 | 257 | no prior successful request for same student_id/course_id |
| 62325 | 6550 | 2696 | DUPLICATE | 400 | 278 | no prior successful request for same student_id/course_id |
| 15798 | 17981 | 58 | DUPLICATE | 400 | 286 | no prior successful request for same student_id/course_id |
| 29615 | 677 | 167 | DUPLICATE | 400 | 299 | no prior successful request for same student_id/course_id |
| 23597 | 11938 | 1890 | DUPLICATE | 400 | 307 | no prior successful request for same student_id/course_id |
| 5230 | 17315 | 171 | DUPLICATE | 400 | 317 | no prior successful request for same student_id/course_id |
| 39301 | 10803 | 97 | DUPLICATE | 400 | 332 | no prior successful request for same student_id/course_id |
| 45972 | 7432 | 3513 | DUPLICATE | 400 | 340 | no prior successful request for same student_id/course_id |
| 69324 | 12566 | 68 | DUPLICATE | 400 | 341 | no prior successful request for same student_id/course_id |
| 54424 | 37810 | 3797 | DUPLICATE | 400 | 354 | no prior successful request for same student_id/course_id |
| 58314 | 2654 | 57 | DUPLICATE | 400 | 362 | no prior successful request for same student_id/course_id |
| 39580 | 25740 | 3288 | DUPLICATE | 400 | 382 | no prior successful request for same student_id/course_id |
| 47698 | 5813 | 118 | DUPLICATE | 400 | 393 | no prior successful request for same student_id/course_id |
| 1157 | 11115 | 117 | DUPLICATE | 400 | 403 | no prior successful request for same student_id/course_id |
| 23582 | 23799 | 300 | DUPLICATE | 400 | 405 | no prior successful request for same student_id/course_id |
| 11253 | 13429 | 95 | DUPLICATE | 400 | 423 | no prior successful request for same student_id/course_id |
| 13550 | 14986 | 1302 | DUPLICATE | 400 | 429 | no prior successful request for same student_id/course_id |
| 63989 | 18295 | 154 | DUPLICATE | 400 | 432 | no prior successful request for same student_id/course_id |
| 832 | 37310 | 199 | DUPLICATE | 400 | 444 | no prior successful request for same student_id/course_id |
| 31726 | 751 | 65 | DUPLICATE | 400 | 447 | no prior successful request for same student_id/course_id |
| 468 | 31528 | 2287 | DUPLICATE | 400 | 448 | no prior successful request for same student_id/course_id |
| 15022 | 27549 | 560 | DUPLICATE | 400 | 448 | no prior successful request for same student_id/course_id |
| 33097 | 34426 | 183 | DUPLICATE | 400 | 455 | no prior successful request for same student_id/course_id |
| 74811 | 20783 | 1062 | DUPLICATE | 400 | 458 | no prior successful request for same student_id/course_id |
| 16245 | 26412 | 1233 | DUPLICATE | 400 | 463 | no prior successful request for same student_id/course_id |
| 77476 | 892 | 97 | DUPLICATE | 400 | 468 | no prior successful request for same student_id/course_id |
| 39266 | 5353 | 539 | DUPLICATE | 400 | 470 | no prior successful request for same student_id/course_id |
| 36288 | 37270 | 3083 | DUPLICATE | 400 | 487 | no prior successful request for same student_id/course_id |
| 17311 | 2419 | 60 | DUPLICATE | 400 | 489 | no prior successful request for same student_id/course_id |
| 45976 | 744 | 154 | DUPLICATE | 400 | 493 | no prior successful request for same student_id/course_id |
| 71 | 26694 | 2529 | DUPLICATE | 400 | 500 | no prior successful request for same student_id/course_id |
| 47118 | 38189 | 113 | DUPLICATE | 400 | 503 | no prior successful request for same student_id/course_id |
| 58804 | 25120 | 1746 | DUPLICATE | 400 | 506 | no prior successful request for same student_id/course_id |
| 66811 | 20936 | 183 | DUPLICATE | 400 | 509 | no prior successful request for same student_id/course_id |
| 44674 | 15681 | 1608 | DUPLICATE | 400 | 512 | no prior successful request for same student_id/course_id |
| 69706 | 33711 | 299 | DUPLICATE | 400 | 522 | no prior successful request for same student_id/course_id |
| 20468 | 20030 | 92 | DUPLICATE | 400 | 524 | no prior successful request for same student_id/course_id |
| 476 | 15395 | 175 | DUPLICATE | 400 | 527 | no prior successful request for same student_id/course_id |
| 8982 | 29496 | 607 | DUPLICATE | 400 | 546 | no prior successful request for same student_id/course_id |
| 32391 | 35158 | 2222 | DUPLICATE | 400 | 551 | no prior successful request for same student_id/course_id |
| 26648 | 3500 | 84 | DUPLICATE | 400 | 558 | no prior successful request for same student_id/course_id |
| 856 | 2883 | 130 | DUPLICATE | 400 | 562 | no prior successful request for same student_id/course_id |
| 26129 | 37701 | 195 | DUPLICATE | 400 | 562 | no prior successful request for same student_id/course_id |
| 37188 | 19641 | 3853 | DUPLICATE | 400 | 571 | no prior successful request for same student_id/course_id |
| 38018 | 21906 | 2777 | DUPLICATE | 400 | 574 | no prior successful request for same student_id/course_id |
| 15921 | 6284 | 193 | DUPLICATE | 400 | 590 | no prior successful request for same student_id/course_id |
| 62384 | 3785 | 140 | DUPLICATE | 400 | 591 | no prior successful request for same student_id/course_id |
| 61721 | 19630 | 72 | DUPLICATE | 400 | 592 | no prior successful request for same student_id/course_id |
| 36608 | 33950 | 277 | DUPLICATE | 400 | 596 | no prior successful request for same student_id/course_id |
| 77813 | 2465 | 3362 | DUPLICATE | 400 | 598 | no prior successful request for same student_id/course_id |
| 53202 | 1767 | 2801 | DUPLICATE | 400 | 602 | no prior successful request for same student_id/course_id |
