# TIME_CONFLICT Payload Validation

Result: **FAIL**

TIME_CONFLICT payloads must overlap an already successful course for the same student.

- Failure count: 2,050

## Failure samples (top 100)

| request_id | student_id | course_id | scenario_type | expected_status | scheduled_offset_ms | reason |
|---:|---:|---:|---|---:|---:|---|
| 39553 | 35101 | 183 | TIME_CONFLICT | 400 | 0 | no prior successful course for student |
| 34530 | 31716 | 1552 | TIME_CONFLICT | 400 | 3 | no prior successful course for student |
| 16275 | 19814 | 2784 | TIME_CONFLICT | 400 | 4 | no prior successful course for student |
| 65105 | 1051 | 143 | TIME_CONFLICT | 400 | 7 | no prior successful course for student |
| 23852 | 5833 | 93 | TIME_CONFLICT | 400 | 20 | no prior successful course for student |
| 45305 | 312 | 32 | TIME_CONFLICT | 400 | 21 | no prior successful course for student |
| 35354 | 25759 | 154 | TIME_CONFLICT | 400 | 41 | no prior successful course for student |
| 71380 | 2662 | 39 | TIME_CONFLICT | 400 | 43 | no prior successful course for student |
| 3561 | 9749 | 3434 | TIME_CONFLICT | 400 | 52 | no prior successful course for student |
| 62001 | 4667 | 29 | TIME_CONFLICT | 400 | 58 | no prior successful course for student |
| 13588 | 17165 | 88 | TIME_CONFLICT | 400 | 60 | no prior successful course for student |
| 9565 | 13495 | 154 | TIME_CONFLICT | 400 | 61 | no prior successful course for student |
| 76081 | 14374 | 197 | TIME_CONFLICT | 400 | 62 | no prior successful course for student |
| 78098 | 37120 | 2894 | TIME_CONFLICT | 400 | 67 | no prior successful course for student |
| 36762 | 23865 | 159 | TIME_CONFLICT | 400 | 77 | no prior successful course for student |
| 37612 | 16137 | 355 | TIME_CONFLICT | 400 | 92 | no prior successful course for student |
| 78450 | 5862 | 3629 | TIME_CONFLICT | 400 | 114 | no prior successful course for student |
| 34400 | 25845 | 2718 | TIME_CONFLICT | 400 | 117 | no prior successful course for student |
| 28137 | 11139 | 160 | TIME_CONFLICT | 400 | 119 | no prior successful course for student |
| 13845 | 28729 | 1014 | TIME_CONFLICT | 400 | 124 | no prior successful course for student |
| 79547 | 34553 | 1297 | TIME_CONFLICT | 400 | 127 | no prior successful course for student |
| 21082 | 29241 | 175 | TIME_CONFLICT | 400 | 128 | no prior successful course for student |
| 75236 | 2398 | 118 | TIME_CONFLICT | 400 | 128 | no prior successful course for student |
| 60467 | 38123 | 3825 | TIME_CONFLICT | 400 | 145 | no prior successful course for student |
| 20009 | 11806 | 2419 | TIME_CONFLICT | 400 | 151 | no prior successful course for student |
| 11231 | 6142 | 709 | TIME_CONFLICT | 400 | 152 | no prior successful course for student |
| 13259 | 30042 | 132 | TIME_CONFLICT | 400 | 178 | no prior successful course for student |
| 15794 | 13573 | 259 | TIME_CONFLICT | 400 | 189 | no prior successful course for student |
| 33284 | 5453 | 19 | TIME_CONFLICT | 400 | 189 | no prior successful course for student |
| 26694 | 33432 | 3312 | TIME_CONFLICT | 400 | 193 | no prior successful course for student |
| 77976 | 19311 | 1679 | TIME_CONFLICT | 400 | 193 | no prior successful course for student |
| 10107 | 3696 | 1214 | TIME_CONFLICT | 400 | 198 | no prior successful course for student |
| 25825 | 39110 | 194 | TIME_CONFLICT | 400 | 198 | no prior successful course for student |
| 67346 | 32380 | 39 | TIME_CONFLICT | 400 | 216 | no prior successful course for student |
| 25296 | 14362 | 1249 | TIME_CONFLICT | 400 | 218 | no prior successful course for student |
| 218 | 5234 | 149 | TIME_CONFLICT | 400 | 234 | no prior successful course for student |
| 11493 | 31782 | 745 | TIME_CONFLICT | 400 | 248 | no prior successful course for student |
| 51508 | 10032 | 1863 | TIME_CONFLICT | 400 | 251 | no prior successful course for student |
| 70220 | 5047 | 669 | TIME_CONFLICT | 400 | 254 | no prior successful course for student |
| 65200 | 27608 | 190 | TIME_CONFLICT | 400 | 262 | no overlapping prior successful course |
| 77643 | 21686 | 167 | TIME_CONFLICT | 400 | 285 | no prior successful course for student |
| 18930 | 27026 | 85 | TIME_CONFLICT | 400 | 288 | no prior successful course for student |
| 39939 | 39655 | 2828 | TIME_CONFLICT | 400 | 292 | no prior successful course for student |
| 49146 | 30572 | 1057 | TIME_CONFLICT | 400 | 295 | no prior successful course for student |
| 62857 | 19219 | 85 | TIME_CONFLICT | 400 | 296 | no prior successful course for student |
| 9331 | 27725 | 817 | TIME_CONFLICT | 400 | 297 | no prior successful course for student |
| 23429 | 12623 | 20 | TIME_CONFLICT | 400 | 306 | no prior successful course for student |
| 52522 | 24526 | 117 | TIME_CONFLICT | 400 | 309 | no prior successful course for student |
| 65462 | 17919 | 192 | TIME_CONFLICT | 400 | 309 | no prior successful course for student |
| 78271 | 28934 | 2240 | TIME_CONFLICT | 400 | 320 | no prior successful course for student |
| 44591 | 7118 | 148 | TIME_CONFLICT | 400 | 321 | no prior successful course for student |
| 33763 | 33242 | 175 | TIME_CONFLICT | 400 | 332 | no prior successful course for student |
| 4255 | 2677 | 94 | TIME_CONFLICT | 400 | 361 | no prior successful course for student |
| 16934 | 38918 | 157 | TIME_CONFLICT | 400 | 369 | no prior successful course for student |
| 55790 | 26539 | 628 | TIME_CONFLICT | 400 | 379 | no prior successful course for student |
| 49153 | 8121 | 7 | TIME_CONFLICT | 400 | 381 | no prior successful course for student |
| 52971 | 36579 | 5 | TIME_CONFLICT | 400 | 386 | no prior successful course for student |
| 68786 | 9113 | 14 | TIME_CONFLICT | 400 | 386 | no prior successful course for student |
| 75386 | 34073 | 162 | TIME_CONFLICT | 400 | 393 | no prior successful course for student |
| 54592 | 34957 | 193 | TIME_CONFLICT | 400 | 394 | no prior successful course for student |
| 67799 | 29288 | 2128 | TIME_CONFLICT | 400 | 396 | no prior successful course for student |
| 13831 | 15231 | 190 | TIME_CONFLICT | 400 | 399 | no prior successful course for student |
| 2170 | 7920 | 108 | TIME_CONFLICT | 400 | 408 | no prior successful course for student |
| 55719 | 39628 | 33 | TIME_CONFLICT | 400 | 409 | no prior successful course for student |
| 15028 | 14106 | 799 | TIME_CONFLICT | 400 | 411 | no prior successful course for student |
| 78910 | 16826 | 93 | TIME_CONFLICT | 400 | 413 | no prior successful course for student |
| 62254 | 6343 | 194 | TIME_CONFLICT | 400 | 414 | no prior successful course for student |
| 9554 | 7377 | 2325 | TIME_CONFLICT | 400 | 425 | no prior successful course for student |
| 67299 | 21025 | 903 | TIME_CONFLICT | 400 | 425 | no prior successful course for student |
| 23424 | 13983 | 27 | TIME_CONFLICT | 400 | 428 | no prior successful course for student |
| 24430 | 29649 | 132 | TIME_CONFLICT | 400 | 430 | no prior successful course for student |
| 46499 | 32227 | 2212 | TIME_CONFLICT | 400 | 431 | no prior successful course for student |
| 13282 | 5323 | 29 | TIME_CONFLICT | 400 | 432 | no prior successful course for student |
| 22456 | 21357 | 442 | TIME_CONFLICT | 400 | 443 | no prior successful course for student |
| 31529 | 11202 | 125 | TIME_CONFLICT | 400 | 448 | no prior successful course for student |
| 11320 | 4915 | 2378 | TIME_CONFLICT | 400 | 450 | no prior successful course for student |
| 16498 | 2815 | 129 | TIME_CONFLICT | 400 | 463 | no prior successful course for student |
| 17121 | 32168 | 507 | TIME_CONFLICT | 400 | 468 | no prior successful course for student |
| 60709 | 9972 | 195 | TIME_CONFLICT | 400 | 470 | no prior successful course for student |
| 15092 | 15450 | 908 | TIME_CONFLICT | 400 | 472 | no prior successful course for student |
| 69562 | 2784 | 169 | TIME_CONFLICT | 400 | 488 | no prior successful course for student |
| 65941 | 30038 | 732 | TIME_CONFLICT | 400 | 490 | no prior successful course for student |
| 11989 | 37160 | 3 | TIME_CONFLICT | 400 | 491 | no prior successful course for student |
| 63783 | 25206 | 43 | TIME_CONFLICT | 400 | 492 | no prior successful course for student |
| 63824 | 22333 | 136 | TIME_CONFLICT | 400 | 520 | no prior successful course for student |
| 15532 | 8392 | 135 | TIME_CONFLICT | 400 | 523 | no overlapping prior successful course |
| 25695 | 21072 | 159 | TIME_CONFLICT | 400 | 532 | no prior successful course for student |
| 70240 | 34449 | 3228 | TIME_CONFLICT | 400 | 539 | no prior successful course for student |
| 79586 | 24046 | 2048 | TIME_CONFLICT | 400 | 559 | no prior successful course for student |
| 54216 | 9639 | 1602 | TIME_CONFLICT | 400 | 561 | no prior successful course for student |
| 11952 | 34766 | 175 | TIME_CONFLICT | 400 | 568 | no prior successful course for student |
| 13825 | 29398 | 27 | TIME_CONFLICT | 400 | 584 | no prior successful course for student |
| 49883 | 15478 | 3472 | TIME_CONFLICT | 400 | 587 | no prior successful course for student |
| 62301 | 27899 | 132 | TIME_CONFLICT | 400 | 587 | no prior successful course for student |
| 24328 | 30129 | 163 | TIME_CONFLICT | 400 | 593 | no prior successful course for student |
| 78435 | 39154 | 392 | TIME_CONFLICT | 400 | 596 | no prior successful course for student |
| 62339 | 16749 | 90 | TIME_CONFLICT | 400 | 611 | no overlapping prior successful course |
| 20750 | 6271 | 467 | TIME_CONFLICT | 400 | 616 | no prior successful course for student |
| 70860 | 20176 | 3722 | TIME_CONFLICT | 400 | 617 | no prior successful course for student |
| 60189 | 11029 | 118 | TIME_CONFLICT | 400 | 624 | no prior successful course for student |
