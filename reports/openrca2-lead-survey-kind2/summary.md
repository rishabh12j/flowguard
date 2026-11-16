# Baseline run: claude:claude-haiku-5-5, 100 development cases

| Score | Mean |
|---|---|
| f1 | 0.722 |
| precision | 0.720 |
| recall | 0.725 |
| acc | 0.710 |
| any_hit | 0.970 |
| all_hit | 0.960 |
| type_acc | 0.747 |
| node_f1 | 0.943 |
| edge_f1 | 0.889 |
| path_acc | 0.747 |
| path_acc_service | 0.989 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-011 | ts | 17 | 16 | 646,361 | 26,789 | 0.039 | 128 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-012 | hs | 14 | 10 | 333,401 | 18,437 | 0.026 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-021 | ts | 36 | 25 | 1,421,409 | 28,686 | 0.054 | 139 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-036 | hs | 15 | 14 | 522,017 | 25,468 | 0.033 | 120 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-038 | ts | 16 | 17 | 786,214 | 24,387 | 0.040 | 117 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-046 | hs | 15 | 11 | 231,538 | 15,932 | 0.020 | 76 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-056 | hs | 19 | 12 | 426,288 | 33,788 | 0.038 | 162 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-059 | otel-demo | 22 | 15 | 581,088 | 26,856 | 0.037 | 122 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-065 | hs | 16 | 15 | 454,321 | 20,470 | 0.029 | 102 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-073 | ts | 13 | 10 | 336,362 | 15,146 | 0.024 | 75 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-079 | hs | 19 | 14 | 444,981 | 16,764 | 0.027 | 85 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-080 | ts | 13 | 11 | 305,605 | 16,191 | 0.022 | 81 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-083 | hs | 11 | 9 | 298,771 | 15,982 | 0.021 | 80 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-084 | ts | 17 | 12 | 420,006 | 29,032 | 0.033 | 132 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-086 | hs | 24 | 21 | 600,750 | 24,769 | 0.033 | 118 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-089 | hs | 12 | 10 | 315,800 | 16,494 | 0.026 | 81 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-092 | ts | 21 | 19 | 742,712 | 29,784 | 0.041 | 142 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-093 | hs | 15 | 12 | 343,839 | 16,942 | 0.026 | 81 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-095 | ts | 22 | 15 | 808,116 | 28,888 | 0.046 | 138 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-103 | hs | 28 | 22 | 860,808 | 24,515 | 0.041 | 122 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-106 | ts | 20 | 17 | 917,298 | 30,139 | 0.047 | 139 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-117 | ts | 25 | 17 | 871,477 | 26,827 | 0.045 | 127 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-120 | ts | 23 | 17 | 935,093 | 37,742 | 0.052 | 178 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-123 | ts | 12 | 9 | 387,018 | 19,236 | 0.030 | 92 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-124 | ts | 26 | 22 | 1,134,242 | 34,897 | 0.053 | 153 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-125 | ts | 15 | 11 | 402,556 | 24,254 | 0.033 | 108 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-126 | hs | 15 | 14 | 357,756 | 22,503 | 0.026 | 109 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-129 | ts | 14 | 10 | 524,947 | 24,301 | 0.035 | 116 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-134 | ts | 15 | 12 | 458,759 | 17,067 | 0.028 | 78 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-146 | ts | 18 | 12 | 618,315 | 26,420 | 0.041 | 120 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-151 | ts | 15 | 17 | 664,054 | 26,953 | 0.039 | 127 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-154 | ts | 11 | 9 | 383,001 | 26,956 | 0.032 | 121 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-155 | otel-demo | 27 | 29 | 1,314,491 | 34,718 | 0.053 | 164 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-164 | hs | 15 | 13 | 429,008 | 18,674 | 0.028 | 92 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-165 | ts | 24 | 18 | 897,157 | 30,889 | 0.048 | 146 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-170 | ts | 43 | 36 | 2,399,361 | 46,226 | 0.208 | 216 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-171 | otel-demo | 28 | 18 | 1,120,215 | 39,098 | 0.062 | 183 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-172 | ts | 27 | 20 | 1,299,323 | 65,872 | 0.080 | 285 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-176 | hs | 15 | 9 | 299,742 | 17,176 | 0.024 | 82 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-179 | hs | 19 | 14 | 572,080 | 23,962 | 0.035 | 112 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-187 | hs | 15 | 13 | 367,076 | 20,118 | 0.028 | 93 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-194 | hs | 13 | 11 | 349,686 | 20,479 | 0.027 | 101 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-195 | ts | 17 | 19 | 901,652 | 32,469 | 0.048 | 155 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-199 | ts | 24 | 19 | 797,269 | 23,837 | 0.040 | 120 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-202 | otel-demo | 18 | 16 | 531,463 | 29,326 | 0.036 | 133 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-203 | ts | 12 | 9 | 327,877 | 19,073 | 0.028 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-208 | ts | 16 | 12 | 503,101 | 29,108 | 0.037 | 132 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-212 | ts | 27 | 20 | 1,084,120 | 35,939 | 0.052 | 168 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-216 | ts | 11 | 9 | 325,286 | 26,137 | 0.030 | 118 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-226 | ts | 23 | 16 | 771,257 | 30,045 | 0.044 | 139 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-233 | hs | 11 | 9 | 264,870 | 15,704 | 0.023 | 75 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-235 | ts | 12 | 10 | 392,059 | 25,162 | 0.031 | 114 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-237 | ts | 17 | 13 | 540,169 | 20,786 | 0.033 | 98 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-240 | hs | 15 | 13 | 311,980 | 18,860 | 0.025 | 92 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-251 | ts | 18 | 15 | 511,563 | 18,886 | 0.029 | 96 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-255 | ts | 20 | 14 | 429,664 | 27,098 | 0.033 | 122 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-256 | ts | 14 | 11 | 385,283 | 24,965 | 0.031 | 115 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-258 | ts | 30 | 23 | 1,372,454 | 42,042 | 0.064 | 204 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-264 | hs | 18 | 13 | 502,046 | 19,353 | 0.031 | 96 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-265 | ts | 26 | 23 | 1,119,181 | 31,722 | 0.050 | 152 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-267 | ts | 34 | 22 | 1,405,219 | 52,308 | 0.074 | 247 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-270 | ts | 12 | 9 | 331,167 | 18,733 | 0.026 | 92 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-274 | ts | 13 | 11 | 607,293 | 35,695 | 0.046 | 148 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-284 | otel-demo | 15 | 11 | 441,462 | 22,671 | 0.031 | 105 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-287 | hs | 23 | 16 | 689,266 | 27,947 | 0.041 | 133 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-296 | ts | 27 | 21 | 839,000 | 40,121 | 0.052 | 178 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-300 | ts | 25 | 19 | 828,919 | 34,303 | 0.045 | 166 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-310 | ts | 27 | 23 | 905,369 | 29,769 | 0.042 | 142 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-311 | hs | 25 | 19 | 877,902 | 29,247 | 0.045 | 146 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-327 | ts | 40 | 32 | 1,854,117 | 45,889 | 0.070 | 217 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-329 | ts | 22 | 19 | 665,889 | 33,561 | 0.041 | 161 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-337 | hs | 28 | 22 | 844,044 | 31,401 | 0.042 | 150 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-339 | ts | 26 | 21 | 1,199,640 | 36,794 | 0.058 | 186 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-340 | ts | 16 | 18 | 778,960 | 38,054 | 0.047 | 166 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-352 | hs | 23 | 19 | 751,268 | 32,401 | 0.044 | 158 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-358 | ts | 18 | 13 | 666,375 | 27,846 | 0.040 | 131 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-359 | hs | 29 | 17 | 739,795 | 38,126 | 0.050 | 182 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-365 | ts | 15 | 13 | 674,417 | 36,097 | 0.044 | 156 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-384 | ts | 9 | 7 | 252,779 | 14,888 | 0.021 | 73 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-387 | ts | 20 | 16 | 544,214 | 30,617 | 0.036 | 143 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-389 | hs | 26 | 20 | 794,520 | 36,866 | 0.048 | 177 | 0 | 0.50 | 1 | the model stopped calling tools |  |
| case-390 | hs | 20 | 15 | 481,833 | 20,479 | 0.029 | 99 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-391 | hs | 13 | 11 | 293,886 | 16,157 | 0.022 | 79 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-395 | ts | 12 | 10 | 407,050 | 18,160 | 0.029 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-398 | otel-demo | 14 | 13 | 621,136 | 30,306 | 0.045 | 148 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-401 | ts | 38 | 39 | 2,497,010 | 41,466 | 0.158 | 204 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-402 | hs | 14 | 9 | 253,237 | 18,856 | 0.024 | 87 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-403 | ts | 27 | 20 | 1,208,319 | 35,284 | 0.059 | 169 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-406 | ts | 25 | 20 | 877,541 | 39,952 | 0.049 | 181 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-414 | hs | 11 | 9 | 249,747 | 20,563 | 0.025 | 101 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-418 | ts | 35 | 34 | 2,257,198 | 74,653 | 0.214 | 333 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-426 | otel-demo | 19 | 20 | 808,007 | 27,138 | 0.042 | 132 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-431 | hs | 16 | 13 | 428,939 | 20,544 | 0.031 | 97 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-432 | hs | 26 | 18 | 845,475 | 27,211 | 0.041 | 130 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-433 | ts | 22 | 22 | 993,659 | 41,106 | 0.055 | 182 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-434 | hs | 14 | 12 | 309,339 | 18,364 | 0.024 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-435 | ts | 46 | 39 | 2,697,117 | 88,480 | 0.140 | 420 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-438 | ts | 18 | 14 | 820,895 | 27,940 | 0.046 | 132 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-442 | ts | 15 | 12 | 413,516 | 24,964 | 0.031 | 113 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-443 | ts | 39 | 40 | 2,612,565 | 56,494 | 0.188 | 279 | 0 | 0.00 | 1 | the model stopped calling tools |  |

Total: $4.57, 74,422,420 prompt tokens, 2,901,790 output tokens.
