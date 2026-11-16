# Baseline run: claude:claude-haiku-5-5, 100 development cases

| Score | Mean |
|---|---|
| f1 | 0.578 |
| precision | 0.575 |
| recall | 0.590 |
| acc | 0.540 |
| any_hit | 0.940 |
| all_hit | 0.930 |
| type_acc | 0.633 |
| node_f1 | 0.911 |
| edge_f1 | 0.836 |
| path_acc | 0.600 |
| path_acc_service | 0.926 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-011 | ts | 38 | 21 | 646,419 | 18,298 | 0.028 | 88 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-012 | hs | 26 | 14 | 391,622 | 12,323 | 0.020 | 60 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-021 | ts | 36 | 21 | 756,407 | 19,802 | 0.031 | 92 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-036 | hs | 24 | 14 | 347,528 | 12,246 | 0.019 | 59 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-038 | ts | 43 | 19 | 708,718 | 21,484 | 0.035 | 100 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-046 | hs | 22 | 11 | 219,954 | 9,721 | 0.015 | 46 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-056 | hs | 34 | 15 | 318,330 | 14,656 | 0.019 | 70 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-059 | otel-demo | 21 | 12 | 385,027 | 11,272 | 0.022 | 54 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-065 | hs | 23 | 13 | 345,975 | 10,890 | 0.018 | 57 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-073 | ts | 19 | 10 | 229,500 | 10,484 | 0.016 | 52 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-079 | hs | 18 | 12 | 266,314 | 9,903 | 0.016 | 49 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-080 | ts | 25 | 12 | 376,745 | 10,928 | 0.022 | 55 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-083 | hs | 21 | 12 | 333,024 | 8,842 | 0.019 | 46 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-084 | ts | 26 | 14 | 370,231 | 19,155 | 0.024 | 84 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-086 | hs | 24 | 14 | 419,952 | 10,872 | 0.021 | 53 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-089 | hs | 19 | 12 | 316,519 | 8,657 | 0.018 | 45 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-092 | ts | 39 | 27 | 1,202,701 | 23,785 | 0.044 | 122 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-093 | hs | 19 | 11 | 254,064 | 8,301 | 0.015 | 42 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-095 | ts | 42 | 19 | 953,381 | 19,803 | 0.041 | 94 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-103 | hs | 21 | 12 | 323,549 | 11,095 | 0.020 | 56 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-106 | ts | 54 | 26 | 1,176,629 | 30,261 | 0.046 | 142 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-117 | ts | 37 | 18 | 709,122 | 20,416 | 0.033 | 94 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-120 | ts | 33 | 29 | 1,180,856 | 23,511 | 0.040 | 120 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-123 | ts | 18 | 10 | 228,232 | 8,393 | 0.015 | 41 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-124 | ts | 25 | 15 | 504,737 | 14,620 | 0.026 | 70 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-125 | ts | 18 | 9 | 219,761 | 12,872 | 0.018 | 55 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-126 | hs | 20 | 13 | 346,736 | 12,274 | 0.019 | 62 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-129 | ts | 24 | 13 | 426,166 | 15,552 | 0.025 | 71 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-134 | ts | 26 | 13 | 298,786 | 11,091 | 0.018 | 53 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-146 | ts | 27 | 17 | 569,073 | 18,400 | 0.028 | 87 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-151 | ts | 24 | 15 | 487,913 | 17,373 | 0.028 | 81 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-154 | ts | 19 | 13 | 441,239 | 13,765 | 0.025 | 66 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-155 | otel-demo | 39 | 20 | 821,256 | 22,483 | 0.036 | 106 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-164 | hs | 20 | 11 | 181,989 | 7,216 | 0.013 | 38 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-165 | ts | 50 | 24 | 1,144,006 | 27,274 | 0.045 | 129 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-170 | ts | 32 | 20 | 745,064 | 21,374 | 0.033 | 103 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-171 | otel-demo | 37 | 19 | 745,237 | 18,125 | 0.033 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-172 | ts | 26 | 13 | 371,447 | 15,238 | 0.024 | 69 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-176 | hs | 32 | 17 | 618,525 | 17,128 | 0.031 | 81 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-179 | hs | 18 | 11 | 265,527 | 7,900 | 0.015 | 39 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-187 | hs | 30 | 15 | 451,219 | 13,016 | 0.023 | 62 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-194 | hs | 28 | 14 | 393,965 | 15,991 | 0.023 | 78 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-195 | ts | 35 | 17 | 750,192 | 17,810 | 0.035 | 85 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-199 | ts | 41 | 19 | 633,761 | 18,958 | 0.031 | 92 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-202 | otel-demo | 23 | 15 | 392,766 | 13,802 | 0.023 | 65 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-203 | ts | 31 | 19 | 666,427 | 16,776 | 0.028 | 81 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-208 | ts | 29 | 22 | 765,750 | 19,064 | 0.032 | 92 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-212 | ts | 30 | 15 | 336,483 | 16,416 | 0.021 | 75 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-216 | ts | 21 | 14 | 389,255 | 14,634 | 0.023 | 66 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-226 | ts | 33 | 16 | 523,245 | 20,146 | 0.028 | 94 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-233 | hs | 26 | 19 | 653,156 | 16,715 | 0.029 | 84 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-235 | ts | 29 | 16 | 588,124 | 19,546 | 0.030 | 90 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-237 | ts | 25 | 14 | 448,529 | 11,921 | 0.023 | 58 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-240 | hs | 22 | 13 | 299,656 | 10,489 | 0.018 | 52 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-251 | ts | 22 | 11 | 285,966 | 12,768 | 0.019 | 61 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-255 | ts | 56 | 29 | 1,528,642 | 30,952 | 0.052 | 149 | 0 | 0.50 | 1 | the model stopped calling tools |  |
| case-256 | ts | 24 | 14 | 499,178 | 13,278 | 0.026 | 66 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-258 | ts | 57 | 27 | 986,501 | 25,579 | 0.038 | 124 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-264 | hs | 23 | 13 | 312,252 | 10,154 | 0.016 | 50 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-265 | ts | 32 | 16 | 553,103 | 15,091 | 0.027 | 75 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-267 | ts | 20 | 14 | 479,418 | 14,694 | 0.025 | 73 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-270 | ts | 40 | 24 | 1,053,575 | 23,783 | 0.042 | 117 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-274 | ts | 20 | 11 | 343,284 | 14,607 | 0.023 | 63 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-284 | otel-demo | 27 | 14 | 447,602 | 15,385 | 0.025 | 69 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-287 | hs | 26 | 14 | 296,698 | 10,553 | 0.016 | 53 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-296 | ts | 34 | 17 | 635,796 | 18,285 | 0.031 | 85 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-300 | ts | 27 | 23 | 934,478 | 18,245 | 0.034 | 92 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-310 | ts | 33 | 17 | 606,642 | 16,527 | 0.030 | 82 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-311 | hs | 39 | 29 | 944,650 | 23,517 | 0.036 | 118 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-327 | ts | 32 | 22 | 764,772 | 17,880 | 0.031 | 91 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-329 | ts | 28 | 16 | 602,165 | 16,963 | 0.030 | 78 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-337 | hs | 22 | 12 | 309,572 | 12,195 | 0.018 | 59 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-339 | ts | 28 | 15 | 524,726 | 15,250 | 0.027 | 74 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-340 | ts | 22 | 12 | 391,051 | 13,536 | 0.024 | 64 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-352 | hs | 27 | 13 | 351,877 | 12,126 | 0.020 | 59 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-358 | ts | 30 | 17 | 792,788 | 20,869 | 0.038 | 100 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-359 | hs | 24 | 13 | 450,666 | 12,599 | 0.025 | 63 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-365 | ts | 27 | 15 | 566,115 | 18,615 | 0.030 | 84 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-384 | ts | 22 | 13 | 267,536 | 10,752 | 0.017 | 52 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-387 | ts | 40 | 29 | 1,302,934 | 27,721 | 0.046 | 136 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-389 | hs | 32 | 20 | 809,464 | 17,941 | 0.034 | 88 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-390 | hs | 17 | 10 | 231,971 | 7,889 | 0.015 | 41 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-391 | hs | 29 | 15 | 441,018 | 13,373 | 0.023 | 67 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-395 | ts | 52 | 30 | 1,458,059 | 27,918 | 0.046 | 132 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-398 | otel-demo | 28 | 16 | 348,948 | 13,827 | 0.019 | 66 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-401 | ts | 51 | 28 | 1,332,741 | 22,167 | 0.045 | 112 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-402 | hs | 14 | 10 | 181,365 | 8,736 | 0.013 | 44 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-403 | ts | 26 | 15 | 563,309 | 17,542 | 0.029 | 83 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-406 | ts | 29 | 17 | 621,641 | 18,815 | 0.030 | 88 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-414 | hs | 29 | 17 | 515,593 | 14,610 | 0.024 | 71 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-418 | ts | 59 | 29 | 2,095,255 | 36,905 | 0.242 | 181 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-426 | otel-demo | 23 | 14 | 300,501 | 13,190 | 0.018 | 63 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-431 | hs | 24 | 13 | 308,377 | 9,122 | 0.017 | 46 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-432 | hs | 29 | 15 | 411,238 | 10,715 | 0.021 | 53 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-433 | ts | 33 | 17 | 608,854 | 23,327 | 0.032 | 106 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-434 | hs | 24 | 13 | 330,876 | 12,341 | 0.019 | 62 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-435 | ts | 70 | 35 | 2,103,341 | 38,830 | 0.191 | 190 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-438 | ts | 32 | 15 | 517,088 | 15,723 | 0.028 | 79 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-442 | ts | 46 | 25 | 1,470,706 | 29,952 | 0.170 | 141 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-443 | ts | 50 | 21 | 928,002 | 23,180 | 0.041 | 107 | 0 | 0.00 | 1 | the model stopped calling tools |  |

Total: $3.18, 59,751,123 prompt tokens, 1,651,094 output tokens.
