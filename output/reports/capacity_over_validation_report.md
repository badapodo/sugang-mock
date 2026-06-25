# CAPACITY_OVER Payload Validation

Result: **FAIL**

CAPACITY_OVER payloads must arrive only after accepted success requests have filled the course capacity.

- Failure count: 3,947

## Failure samples (top 100)

| request_id | student_id | course_id | scenario_type | expected_status | scheduled_offset_ms | reason |
|---:|---:|---:|---|---:|---:|---|
| 56559 | 155 | 184 | CAPACITY_OVER | 400 | 4 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 26909 | 34932 | 187 | CAPACITY_OVER | 400 | 5 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 37491 | 33 | 156 | CAPACITY_OVER | 400 | 6 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 59787 | 20868 | 189 | CAPACITY_OVER | 400 | 7 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 28852 | 28214 | 131 | CAPACITY_OVER | 400 | 9 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 57810 | 4520 | 369 | CAPACITY_OVER | 400 | 12 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 78904 | 38321 | 130 | CAPACITY_OVER | 400 | 12 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 11492 | 29967 | 78 | CAPACITY_OVER | 400 | 13 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 14055 | 8931 | 162 | CAPACITY_OVER | 400 | 15 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 8479 | 31462 | 90 | CAPACITY_OVER | 400 | 17 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 46784 | 11845 | 148 | CAPACITY_OVER | 400 | 21 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 67739 | 26073 | 2395 | CAPACITY_OVER | 400 | 26 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 79066 | 24665 | 2284 | CAPACITY_OVER | 400 | 29 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 5657 | 21439 | 68 | CAPACITY_OVER | 400 | 32 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 16339 | 30708 | 560 | CAPACITY_OVER | 400 | 32 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 72387 | 3400 | 558 | CAPACITY_OVER | 400 | 35 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 60595 | 5377 | 1070 | CAPACITY_OVER | 400 | 37 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 44795 | 37845 | 60 | CAPACITY_OVER | 400 | 40 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 48950 | 9245 | 70 | CAPACITY_OVER | 400 | 40 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 74077 | 34879 | 45 | CAPACITY_OVER | 400 | 41 | capacity not yet exceeded; accepted_success=2, capacity=50 |
| 18361 | 38870 | 91 | CAPACITY_OVER | 400 | 45 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 52799 | 22240 | 3991 | CAPACITY_OVER | 400 | 46 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 57901 | 12324 | 1131 | CAPACITY_OVER | 400 | 46 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 50711 | 2655 | 118 | CAPACITY_OVER | 400 | 51 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 9084 | 32560 | 171 | CAPACITY_OVER | 400 | 52 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 716 | 35935 | 3004 | CAPACITY_OVER | 400 | 54 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 78629 | 11748 | 19 | CAPACITY_OVER | 400 | 54 | capacity not yet exceeded; accepted_success=5, capacity=50 |
| 43382 | 28237 | 63 | CAPACITY_OVER | 400 | 61 | capacity not yet exceeded; accepted_success=2, capacity=50 |
| 29535 | 15911 | 1303 | CAPACITY_OVER | 400 | 64 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 57679 | 18133 | 112 | CAPACITY_OVER | 400 | 66 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 76034 | 3791 | 104 | CAPACITY_OVER | 400 | 68 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 43320 | 29059 | 3116 | CAPACITY_OVER | 400 | 69 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 4918 | 20463 | 47 | CAPACITY_OVER | 400 | 70 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 1832 | 29108 | 291 | CAPACITY_OVER | 400 | 80 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 58583 | 3222 | 2239 | CAPACITY_OVER | 400 | 86 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 9283 | 24521 | 165 | CAPACITY_OVER | 400 | 91 | capacity not yet exceeded; accepted_success=2, capacity=50 |
| 26099 | 23200 | 88 | CAPACITY_OVER | 400 | 92 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 58028 | 19152 | 2834 | CAPACITY_OVER | 400 | 92 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 76405 | 37218 | 101 | CAPACITY_OVER | 400 | 93 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 18006 | 21666 | 172 | CAPACITY_OVER | 400 | 94 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 58241 | 10831 | 53 | CAPACITY_OVER | 400 | 97 | capacity not yet exceeded; accepted_success=3, capacity=50 |
| 65592 | 35010 | 144 | CAPACITY_OVER | 400 | 97 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 9246 | 3979 | 141 | CAPACITY_OVER | 400 | 107 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 44512 | 24498 | 2594 | CAPACITY_OVER | 400 | 110 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 324 | 20369 | 154 | CAPACITY_OVER | 400 | 111 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 28359 | 27570 | 89 | CAPACITY_OVER | 400 | 112 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 63577 | 36782 | 166 | CAPACITY_OVER | 400 | 115 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 19787 | 37433 | 3824 | CAPACITY_OVER | 400 | 116 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 27121 | 8289 | 20 | CAPACITY_OVER | 400 | 116 | capacity not yet exceeded; accepted_success=5, capacity=50 |
| 28385 | 32486 | 131 | CAPACITY_OVER | 400 | 118 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 31515 | 14324 | 19 | CAPACITY_OVER | 400 | 118 | capacity not yet exceeded; accepted_success=6, capacity=50 |
| 50945 | 4772 | 3975 | CAPACITY_OVER | 400 | 119 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 545 | 8226 | 182 | CAPACITY_OVER | 400 | 123 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 63908 | 39408 | 140 | CAPACITY_OVER | 400 | 126 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 16225 | 11085 | 2134 | CAPACITY_OVER | 400 | 128 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 77582 | 22292 | 1912 | CAPACITY_OVER | 400 | 137 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 39576 | 2897 | 2013 | CAPACITY_OVER | 400 | 139 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 2817 | 32258 | 1488 | CAPACITY_OVER | 400 | 140 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 73825 | 21954 | 134 | CAPACITY_OVER | 400 | 140 | capacity not yet exceeded; accepted_success=2, capacity=50 |
| 19078 | 29201 | 187 | CAPACITY_OVER | 400 | 142 | capacity not yet exceeded; accepted_success=4, capacity=50 |
| 57802 | 26233 | 41 | CAPACITY_OVER | 400 | 145 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 41019 | 14780 | 128 | CAPACITY_OVER | 400 | 146 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 35305 | 21895 | 128 | CAPACITY_OVER | 400 | 147 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 64910 | 17676 | 80 | CAPACITY_OVER | 400 | 153 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 18994 | 5446 | 150 | CAPACITY_OVER | 400 | 156 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 31181 | 3241 | 1006 | CAPACITY_OVER | 400 | 157 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 75349 | 2069 | 197 | CAPACITY_OVER | 400 | 161 | capacity not yet exceeded; accepted_success=2, capacity=50 |
| 67396 | 23484 | 144 | CAPACITY_OVER | 400 | 162 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 51850 | 33137 | 15 | CAPACITY_OVER | 400 | 166 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 37926 | 32592 | 187 | CAPACITY_OVER | 400 | 168 | capacity not yet exceeded; accepted_success=4, capacity=50 |
| 49968 | 30537 | 1367 | CAPACITY_OVER | 400 | 174 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 26943 | 27483 | 180 | CAPACITY_OVER | 400 | 175 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 18571 | 3443 | 2780 | CAPACITY_OVER | 400 | 176 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 55673 | 28605 | 67 | CAPACITY_OVER | 400 | 184 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 44679 | 28348 | 371 | CAPACITY_OVER | 400 | 187 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 69386 | 17211 | 170 | CAPACITY_OVER | 400 | 187 | capacity not yet exceeded; accepted_success=4, capacity=50 |
| 5397 | 24394 | 841 | CAPACITY_OVER | 400 | 191 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 48611 | 14178 | 167 | CAPACITY_OVER | 400 | 193 | capacity not yet exceeded; accepted_success=5, capacity=50 |
| 12544 | 15580 | 141 | CAPACITY_OVER | 400 | 195 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 49524 | 31218 | 258 | CAPACITY_OVER | 400 | 195 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 26976 | 35775 | 89 | CAPACITY_OVER | 400 | 204 | capacity not yet exceeded; accepted_success=1, capacity=50 |
| 53871 | 39112 | 144 | CAPACITY_OVER | 400 | 212 | capacity not yet exceeded; accepted_success=3, capacity=50 |
| 15330 | 3125 | 133 | CAPACITY_OVER | 400 | 214 | capacity not yet exceeded; accepted_success=5, capacity=50 |
| 53270 | 5213 | 2701 | CAPACITY_OVER | 400 | 221 | capacity not yet exceeded; accepted_success=1, capacity=100 |
| 10046 | 829 | 801 | CAPACITY_OVER | 400 | 228 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 76855 | 9224 | 114 | CAPACITY_OVER | 400 | 230 | capacity not yet exceeded; accepted_success=4, capacity=50 |
| 2841 | 1827 | 17 | CAPACITY_OVER | 400 | 231 | capacity not yet exceeded; accepted_success=4, capacity=50 |
| 8484 | 37706 | 3991 | CAPACITY_OVER | 400 | 233 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 5323 | 6736 | 164 | CAPACITY_OVER | 400 | 237 | capacity not yet exceeded; accepted_success=3, capacity=50 |
| 44124 | 23007 | 20 | CAPACITY_OVER | 400 | 237 | capacity not yet exceeded; accepted_success=6, capacity=50 |
| 13109 | 32371 | 48 | CAPACITY_OVER | 400 | 239 | capacity not yet exceeded; accepted_success=2, capacity=50 |
| 1909 | 9938 | 137 | CAPACITY_OVER | 400 | 243 | capacity not yet exceeded; accepted_success=2, capacity=50 |
| 1101 | 37322 | 2012 | CAPACITY_OVER | 400 | 244 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 76884 | 16928 | 181 | CAPACITY_OVER | 400 | 247 | capacity not yet exceeded; accepted_success=0, capacity=50 |
| 71111 | 660 | 1011 | CAPACITY_OVER | 400 | 250 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 57948 | 32461 | 2049 | CAPACITY_OVER | 400 | 251 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 42357 | 6439 | 1660 | CAPACITY_OVER | 400 | 252 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 33785 | 18938 | 58 | CAPACITY_OVER | 400 | 257 | capacity not yet exceeded; accepted_success=3, capacity=50 |
| 2823 | 4893 | 3979 | CAPACITY_OVER | 400 | 261 | capacity not yet exceeded; accepted_success=0, capacity=100 |
| 42744 | 16407 | 197 | CAPACITY_OVER | 400 | 279 | capacity not yet exceeded; accepted_success=6, capacity=50 |
