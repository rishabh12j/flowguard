# Baseline run: claude:claude-haiku-5-5, 100 development cases

| Score | Mean |
|---|---|
| f1 | 0.593 |
| precision | 0.590 |
| recall | 0.605 |
| acc | 0.560 |
| any_hit | 0.920 |
| all_hit | 0.900 |
| type_acc | 0.663 |
| node_f1 | 0.890 |
| edge_f1 | 0.801 |
| path_acc | 0.600 |
| path_acc_service | 0.905 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-011 | ts | 36 | 19 | 749,253 | 19,859 | 0.034 | 97 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-012 | hs | 20 | 11 | 198,293 | 8,437 | 0.014 | 41 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-021 | ts | 59 | 33 | 1,513,892 | 31,028 | 0.048 | 149 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-036 | hs | 29 | 16 | 367,269 | 13,344 | 0.019 | 66 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-038 | ts | 42 | 25 | 927,146 | 22,716 | 0.036 | 110 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-046 | hs | 15 | 11 | 242,614 | 10,435 | 0.016 | 50 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-056 | hs | 32 | 17 | 566,037 | 17,565 | 0.028 | 86 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-059 | otel-demo | 20 | 12 | 269,076 | 11,231 | 0.017 | 51 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-065 | hs | 26 | 16 | 456,328 | 13,047 | 0.022 | 62 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-073 | ts | 30 | 17 | 413,980 | 16,128 | 0.022 | 77 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-079 | hs | 24 | 13 | 372,594 | 9,812 | 0.020 | 50 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-080 | ts | 18 | 12 | 314,696 | 11,411 | 0.019 | 54 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-083 | hs | 29 | 15 | 397,091 | 10,616 | 0.019 | 51 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-084 | ts | 34 | 19 | 555,904 | 17,588 | 0.026 | 78 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-086 | hs | 21 | 12 | 284,878 | 10,325 | 0.017 | 50 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-089 | hs | 34 | 16 | 381,594 | 13,463 | 0.021 | 63 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-092 | ts | 45 | 26 | 1,027,223 | 23,982 | 0.039 | 116 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-093 | hs | 23 | 11 | 259,859 | 9,892 | 0.018 | 45 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-095 | ts | 44 | 25 | 942,610 | 21,664 | 0.036 | 103 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-103 | hs | 24 | 12 | 325,482 | 10,710 | 0.019 | 52 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-106 | ts | 43 | 27 | 1,362,820 | 30,637 | 0.048 | 138 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-117 | ts | 38 | 25 | 961,185 | 18,529 | 0.035 | 86 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-120 | ts | 31 | 20 | 749,949 | 19,720 | 0.035 | 91 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-123 | ts | 19 | 13 | 345,012 | 10,214 | 0.019 | 48 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-124 | ts | 30 | 18 | 487,253 | 17,404 | 0.026 | 77 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-125 | ts | 31 | 16 | 392,426 | 15,301 | 0.022 | 67 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-126 | hs | 22 | 12 | 277,053 | 11,644 | 0.018 | 55 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-129 | ts | 30 | 17 | 537,357 | 16,817 | 0.027 | 77 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-134 | ts | 26 | 15 | 452,423 | 14,820 | 0.023 | 69 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-146 | ts | 30 | 16 | 553,537 | 17,855 | 0.028 | 78 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-151 | ts | 35 | 17 | 773,731 | 19,356 | 0.036 | 88 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-154 | ts | 23 | 15 | 378,767 | 12,745 | 0.020 | 60 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-155 | otel-demo | 35 | 20 | 627,695 | 18,645 | 0.030 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-164 | hs | 16 | 12 | 275,766 | 7,420 | 0.015 | 38 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-165 | ts | 33 | 20 | 656,528 | 19,572 | 0.033 | 92 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-170 | ts | 47 | 29 | 1,319,056 | 28,310 | 0.046 | 133 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-171 | otel-demo | 29 | 16 | 515,015 | 13,690 | 0.026 | 63 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-172 | ts | 28 | 16 | 439,700 | 19,481 | 0.026 | 89 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-176 | hs | 30 | 19 | 630,508 | 16,488 | 0.028 | 77 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-179 | hs | 24 | 11 | 265,832 | 9,809 | 0.017 | 46 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-187 | hs | 17 | 12 | 208,096 | 7,597 | 0.012 | 36 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-194 | hs | 28 | 15 | 380,690 | 16,210 | 0.023 | 76 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-195 | ts | 39 | 20 | 619,535 | 20,934 | 0.031 | 92 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-199 | ts | 28 | 18 | 508,908 | 15,006 | 0.025 | 72 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-202 | otel-demo | 30 | 16 | 409,681 | 13,330 | 0.022 | 64 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-203 | ts | 33 | 16 | 580,011 | 18,838 | 0.031 | 84 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-208 | ts | 34 | 21 | 619,339 | 18,538 | 0.028 | 84 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-212 | ts | 37 | 20 | 724,137 | 23,047 | 0.033 | 105 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-216 | ts | 29 | 19 | 526,782 | 16,110 | 0.025 | 77 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-226 | ts | 49 | 22 | 1,073,728 | 27,079 | 0.045 | 125 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-233 | hs | 33 | 15 | 418,292 | 14,232 | 0.022 | 66 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-235 | ts | 44 | 25 | 1,211,892 | 30,884 | 0.047 | 143 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-237 | ts | 31 | 15 | 629,346 | 14,575 | 0.028 | 69 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-240 | hs | 26 | 14 | 418,753 | 10,628 | 0.020 | 52 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-251 | ts | 26 | 15 | 398,355 | 13,840 | 0.022 | 66 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-255 | ts | 65 | 34 | 2,277,176 | 38,169 | 0.205 | 179 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-256 | ts | 28 | 19 | 415,718 | 13,006 | 0.020 | 66 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-258 | ts | 70 | 37 | 1,552,167 | 26,806 | 0.048 | 130 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-264 | hs | 21 | 11 | 242,888 | 8,092 | 0.015 | 40 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-265 | ts | 31 | 17 | 589,439 | 15,679 | 0.027 | 75 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-267 | ts | 59 | 30 | 1,801,742 | 34,964 | 0.193 | 164 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-270 | ts | 34 | 16 | 519,903 | 16,788 | 0.027 | 78 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-274 | ts | 28 | 13 | 475,514 | 16,224 | 0.027 | 71 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-284 | otel-demo | 22 | 13 | 326,909 | 12,296 | 0.020 | 57 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-287 | hs | 20 | 12 | 261,230 | 9,275 | 0.015 | 44 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-296 | ts | 32 | 14 | 540,765 | 15,789 | 0.028 | 73 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-300 | ts | 44 | 20 | 813,995 | 21,302 | 0.035 | 102 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-310 | ts | 44 | 28 | 1,165,453 | 24,557 | 0.041 | 116 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-311 | hs | 20 | 12 | 310,133 | 10,371 | 0.018 | 50 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-327 | ts | 37 | 24 | 1,059,110 | 21,435 | 0.039 | 101 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-329 | ts | 31 | 17 | 606,838 | 19,665 | 0.032 | 87 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-337 | hs | 27 | 21 | 754,477 | 16,529 | 0.030 | 85 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-339 | ts | 32 | 18 | 669,514 | 16,932 | 0.030 | 82 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-340 | ts | 30 | 15 | 415,988 | 15,345 | 0.023 | 70 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-352 | hs | 29 | 16 | 407,949 | 14,674 | 0.021 | 67 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-358 | ts | 38 | 16 | 674,137 | 18,907 | 0.032 | 85 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-359 | hs | 20 | 11 | 199,783 | 8,537 | 0.014 | 43 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-365 | ts | 20 | 12 | 301,053 | 13,639 | 0.020 | 59 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-384 | ts | 26 | 18 | 525,901 | 15,292 | 0.025 | 74 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-387 | ts | 26 | 16 | 449,391 | 16,327 | 0.023 | 72 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-389 | hs | 31 | 17 | 509,302 | 20,194 | 0.028 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-390 | hs | 30 | 15 | 428,695 | 11,651 | 0.022 | 57 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-391 | hs | 44 | 23 | 806,586 | 18,785 | 0.032 | 94 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-395 | ts | 57 | 29 | 1,268,082 | 32,079 | 0.048 | 152 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-398 | otel-demo | 34 | 19 | 665,407 | 17,380 | 0.030 | 83 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-401 | ts | 35 | 21 | 762,830 | 16,893 | 0.031 | 83 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-402 | hs | 22 | 11 | 206,487 | 9,251 | 0.015 | 45 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-403 | ts | 38 | 23 | 825,384 | 18,044 | 0.033 | 88 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-406 | ts | 24 | 12 | 386,183 | 13,146 | 0.022 | 61 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-414 | hs | 32 | 16 | 650,816 | 16,750 | 0.031 | 82 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-418 | ts | 79 | 42 | 2,698,469 | 40,383 | 0.213 | 195 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-426 | otel-demo | 36 | 20 | 527,254 | 12,601 | 0.022 | 66 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-431 | hs | 31 | 20 | 795,063 | 13,529 | 0.029 | 68 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-432 | hs | 21 | 13 | 289,681 | 9,218 | 0.017 | 47 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-433 | ts | 36 | 20 | 754,971 | 24,137 | 0.037 | 110 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-434 | hs | 18 | 17 | 437,412 | 11,812 | 0.020 | 60 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-435 | ts | 30 | 18 | 617,460 | 14,065 | 0.029 | 68 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-438 | ts | 33 | 17 | 601,950 | 16,939 | 0.029 | 79 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-442 | ts | 40 | 21 | 727,158 | 21,042 | 0.032 | 101 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-443 | ts | 37 | 19 | 892,378 | 23,209 | 0.041 | 104 | 1 | 1.00 | 1 | the model stopped calling tools |  |

Total: $3.23, 63,503,718 prompt tokens, 1,704,266 output tokens.
