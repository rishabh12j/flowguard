# Baseline run: claude:claude-haiku-5-5, 100 development cases

| Score | Mean |
|---|---|
| f1 | 0.565 |
| precision | 0.555 |
| recall | 0.590 |
| acc | 0.500 |
| any_hit | 0.940 |
| all_hit | 0.920 |
| type_acc | 0.633 |
| node_f1 | 0.876 |
| edge_f1 | 0.810 |
| path_acc | 0.589 |
| path_acc_service | 0.937 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-011 | ts | 25 | 26 | 986,930 | 19,382 | 0.035 | 87 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-012 | hs | 23 | 24 | 823,684 | 14,028 | 0.029 | 66 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-021 | ts | 42 | 29 | 1,792,283 | 32,246 | 0.138 | 145 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-036 | hs | 29 | 24 | 826,938 | 18,906 | 0.031 | 86 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-038 | ts | 16 | 16 | 437,787 | 14,315 | 0.023 | 62 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-046 | hs | 20 | 13 | 306,796 | 11,519 | 0.017 | 52 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-056 | hs | 15 | 11 | 239,562 | 9,233 | 0.016 | 43 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-059 | otel-demo | 19 | 18 | 549,948 | 18,513 | 0.027 | 84 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-065 | hs | 16 | 14 | 340,886 | 12,729 | 0.019 | 57 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-073 | ts | 21 | 22 | 624,060 | 14,939 | 0.026 | 71 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-079 | hs | 17 | 14 | 306,278 | 12,220 | 0.017 | 56 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-080 | ts | 13 | 12 | 270,957 | 8,453 | 0.016 | 39 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-083 | hs | 17 | 10 | 321,868 | 9,972 | 0.021 | 45 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-084 | ts | 18 | 15 | 506,228 | 15,685 | 0.026 | 67 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-086 | hs | 15 | 13 | 308,059 | 9,779 | 0.016 | 46 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-089 | hs | 18 | 14 | 345,271 | 10,906 | 0.017 | 51 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-092 | ts | 30 | 27 | 1,711,284 | 25,352 | 0.135 | 123 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-093 | hs | 20 | 16 | 382,846 | 10,128 | 0.018 | 48 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-095 | ts | 29 | 28 | 1,371,798 | 23,276 | 0.046 | 110 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-103 | hs | 25 | 24 | 947,264 | 18,459 | 0.035 | 88 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-106 | ts | 27 | 21 | 776,440 | 18,068 | 0.031 | 80 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-117 | ts | 29 | 29 | 1,429,359 | 25,855 | 0.045 | 120 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-120 | ts | 36 | 35 | 2,010,819 | 30,671 | 0.160 | 144 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-123 | ts | 20 | 14 | 509,461 | 11,407 | 0.025 | 53 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-124 | ts | 21 | 15 | 523,069 | 18,545 | 0.027 | 76 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-125 | ts | 14 | 15 | 321,583 | 13,749 | 0.019 | 59 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-126 | hs | 19 | 18 | 455,588 | 14,837 | 0.021 | 72 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-129 | ts | 45 | 38 | 2,641,979 | 41,310 | 0.209 | 190 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-134 | ts | 19 | 14 | 260,670 | 9,332 | 0.015 | 44 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-146 | ts | 20 | 18 | 592,565 | 19,936 | 0.031 | 83 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-151 | ts | 26 | 23 | 1,406,412 | 20,893 | 0.148 | 96 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-154 | ts | 19 | 20 | 807,288 | 19,257 | 0.034 | 81 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-155 | otel-demo | 33 | 29 | 1,906,553 | 27,400 | 0.159 | 128 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-164 | hs | 20 | 15 | 467,060 | 11,102 | 0.021 | 51 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-165 | ts | 33 | 27 | 1,361,406 | 26,453 | 0.048 | 123 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-170 | ts | 27 | 19 | 1,033,359 | 28,239 | 0.120 | 128 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-171 | otel-demo | 36 | 28 | 1,501,074 | 28,000 | 0.107 | 128 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-172 | ts | 27 | 23 | 856,905 | 25,947 | 0.037 | 108 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-176 | hs | 12 | 12 | 267,704 | 7,862 | 0.014 | 37 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-179 | hs | 19 | 15 | 454,759 | 11,524 | 0.022 | 52 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-187 | hs | 22 | 23 | 761,647 | 16,891 | 0.029 | 80 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-194 | hs | 19 | 16 | 423,289 | 12,677 | 0.020 | 59 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-195 | ts | 20 | 21 | 865,025 | 22,355 | 0.037 | 99 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-199 | ts | 30 | 25 | 1,194,427 | 21,435 | 0.043 | 101 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-202 | otel-demo | 18 | 19 | 547,187 | 14,263 | 0.023 | 65 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-203 | ts | 16 | 15 | 366,594 | 11,606 | 0.018 | 52 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-208 | ts | 17 | 18 | 680,549 | 19,175 | 0.031 | 84 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-212 | ts | 34 | 32 | 1,767,406 | 25,669 | 0.109 | 122 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-216 | ts | 27 | 18 | 743,201 | 17,018 | 0.032 | 76 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-226 | ts | 26 | 27 | 1,023,755 | 21,615 | 0.037 | 102 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-233 | hs | 11 | 12 | 251,896 | 9,420 | 0.014 | 43 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-235 | ts | 17 | 17 | 653,952 | 20,751 | 0.031 | 90 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-237 | ts | 20 | 16 | 425,870 | 13,293 | 0.023 | 57 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-240 | hs | 16 | 15 | 416,752 | 11,323 | 0.019 | 53 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-251 | ts | 14 | 15 | 428,164 | 15,454 | 0.024 | 70 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-255 | ts | 16 | 14 | 475,149 | 13,516 | 0.025 | 60 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-256 | ts | 23 | 18 | 571,583 | 12,127 | 0.025 | 58 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-258 | ts | 41 | 34 | 2,628,969 | 26,615 | 0.235 | 132 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-264 | hs | 19 | 14 | 338,420 | 10,414 | 0.018 | 48 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-265 | ts | 22 | 15 | 389,390 | 12,522 | 0.019 | 55 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-267 | ts | 30 | 26 | 1,329,837 | 19,890 | 0.044 | 100 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-270 | ts | 24 | 24 | 924,783 | 16,531 | 0.035 | 80 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-274 | ts | 17 | 17 | 626,947 | 16,125 | 0.028 | 68 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-284 | otel-demo | 20 | 14 | 461,461 | 14,546 | 0.025 | 61 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-287 | hs | 24 | 17 | 587,233 | 15,015 | 0.027 | 70 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-296 | ts | 20 | 16 | 446,990 | 14,335 | 0.023 | 63 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-300 | ts | 26 | 18 | 736,048 | 20,626 | 0.034 | 89 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-310 | ts | 21 | 22 | 886,931 | 16,607 | 0.032 | 78 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-311 | hs | 32 | 28 | 1,223,986 | 26,358 | 0.043 | 126 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-327 | ts | 41 | 33 | 1,585,326 | 32,773 | 0.052 | 152 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-329 | ts | 23 | 16 | 600,546 | 18,891 | 0.031 | 81 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-337 | hs | 16 | 14 | 325,517 | 12,683 | 0.018 | 57 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-339 | ts | 44 | 41 | 2,933,430 | 37,617 | 0.260 | 177 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-340 | ts | 17 | 13 | 493,635 | 14,495 | 0.027 | 61 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-352 | hs | 29 | 17 | 561,536 | 16,199 | 0.028 | 74 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-358 | ts | 29 | 26 | 1,079,831 | 20,320 | 0.038 | 93 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-359 | hs | 25 | 17 | 538,781 | 15,294 | 0.026 | 70 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-365 | ts | 18 | 17 | 484,551 | 23,082 | 0.029 | 95 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-384 | ts | 21 | 17 | 586,474 | 13,593 | 0.025 | 62 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-387 | ts | 29 | 30 | 1,448,796 | 29,424 | 0.048 | 136 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-389 | hs | 23 | 16 | 480,546 | 18,408 | 0.027 | 78 | 0 | 0.50 | 1 | the model stopped calling tools |  |
| case-390 | hs | 17 | 15 | 352,744 | 11,687 | 0.018 | 55 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-391 | hs | 19 | 15 | 447,408 | 11,065 | 0.020 | 52 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-395 | ts | 33 | 27 | 1,324,194 | 26,132 | 0.046 | 119 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-398 | otel-demo | 24 | 21 | 717,125 | 15,170 | 0.029 | 70 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-401 | ts | 35 | 35 | 2,139,856 | 32,503 | 0.178 | 152 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-402 | hs | 22 | 16 | 455,214 | 13,761 | 0.023 | 62 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-403 | ts | 27 | 23 | 908,547 | 16,620 | 0.032 | 75 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-406 | ts | 23 | 15 | 654,928 | 19,621 | 0.034 | 82 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-414 | hs | 9 | 9 | 178,459 | 8,396 | 0.013 | 41 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-418 | ts | 49 | 44 | 3,053,615 | 40,326 | 0.262 | 191 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-426 | otel-demo | 20 | 14 | 424,737 | 13,588 | 0.021 | 61 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-431 | hs | 15 | 10 | 242,723 | 9,395 | 0.016 | 42 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-432 | hs | 26 | 19 | 585,395 | 11,318 | 0.022 | 54 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-433 | ts | 23 | 14 | 488,989 | 15,508 | 0.026 | 69 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-434 | hs | 20 | 17 | 534,812 | 13,520 | 0.023 | 66 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-435 | ts | 42 | 33 | 2,258,430 | 40,587 | 0.239 | 190 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-438 | ts | 28 | 26 | 970,021 | 16,403 | 0.033 | 80 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-442 | ts | 33 | 29 | 1,376,347 | 28,281 | 0.048 | 130 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-443 | ts | 49 | 43 | 2,722,981 | 46,984 | 0.266 | 216 | 1 | 1.00 | 1 | the model stopped calling tools |  |

Total: $5.06, 86,117,715 prompt tokens, 1,852,243 output tokens.
