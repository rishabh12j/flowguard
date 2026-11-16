# Baseline run: claude:claude-haiku-5-5, 100 development cases

| Score | Mean |
|---|---|
| f1 | 0.693 |
| precision | 0.690 |
| recall | 0.705 |
| acc | 0.660 |
| any_hit | 1.000 |
| all_hit | 0.980 |
| type_acc | 0.710 |
| node_f1 | 0.943 |
| edge_f1 | 0.905 |
| path_acc | 0.705 |
| path_acc_service | 1.000 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-011 | ts | 17 | 17 | 894,130 | 46,856 | 0.059 | 200 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-012 | hs | 16 | 13 | 492,626 | 24,885 | 0.035 | 123 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-021 | ts | 34 | 30 | 2,097,737 | 46,457 | 0.136 | 216 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-036 | hs | 18 | 16 | 631,746 | 28,430 | 0.039 | 137 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-038 | ts | 15 | 11 | 713,026 | 32,143 | 0.048 | 144 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-046 | hs | 13 | 10 | 397,642 | 23,098 | 0.032 | 110 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-056 | hs | 14 | 11 | 432,882 | 26,441 | 0.035 | 128 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-059 | otel-demo | 22 | 17 | 653,372 | 35,845 | 0.048 | 163 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-065 | hs | 15 | 12 | 512,558 | 30,395 | 0.039 | 145 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-073 | ts | 16 | 14 | 610,748 | 34,714 | 0.043 | 155 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-079 | hs | 29 | 21 | 1,095,057 | 59,354 | 0.071 | 284 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-080 | ts | 13 | 11 | 592,856 | 28,706 | 0.040 | 138 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-083 | hs | 15 | 12 | 390,743 | 19,487 | 0.028 | 92 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-084 | ts | 15 | 12 | 727,231 | 60,020 | 0.065 | 231 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-086 | hs | 17 | 12 | 627,303 | 27,874 | 0.038 | 134 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-089 | hs | 27 | 17 | 566,317 | 26,263 | 0.036 | 128 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-092 | ts | 33 | 21 | 1,100,645 | 48,263 | 0.063 | 237 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-093 | hs | 15 | 10 | 447,777 | 24,969 | 0.034 | 119 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-095 | ts | 17 | 15 | 611,854 | 42,520 | 0.049 | 185 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-103 | hs | 36 | 30 | 1,775,218 | 52,116 | 0.075 | 252 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-106 | ts | 16 | 17 | 606,379 | 32,375 | 0.040 | 146 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-117 | ts | 27 | 22 | 1,290,126 | 32,676 | 0.056 | 157 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-120 | ts | 43 | 28 | 2,182,660 | 62,758 | 0.248 | 282 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-123 | ts | 13 | 12 | 723,036 | 35,038 | 0.048 | 165 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-124 | ts | 19 | 15 | 1,433,304 | 64,437 | 0.091 | 282 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-125 | ts | 9 | 10 | 483,199 | 35,996 | 0.044 | 148 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-126 | hs | 11 | 9 | 251,656 | 26,199 | 0.027 | 122 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-129 | ts | 21 | 18 | 1,004,178 | 39,330 | 0.058 | 178 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-134 | ts | 17 | 12 | 434,359 | 18,931 | 0.030 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-146 | ts | 12 | 8 | 670,847 | 51,680 | 0.057 | 210 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-151 | ts | 21 | 18 | 1,142,766 | 55,506 | 0.069 | 243 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-154 | ts | 18 | 19 | 862,342 | 45,672 | 0.057 | 194 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-155 | otel-demo | 29 | 28 | 1,607,087 | 82,567 | 0.117 | 368 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-164 | hs | 16 | 13 | 502,099 | 23,786 | 0.034 | 117 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-165 | ts | 25 | 16 | 855,967 | 38,417 | 0.053 | 180 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-170 | ts | 22 | 18 | 958,838 | 42,283 | 0.058 | 186 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-171 | otel-demo | 34 | 24 | 1,325,707 | 62,517 | 0.081 | 292 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-172 | ts | 24 | 25 | 1,412,699 | 63,335 | 0.077 | 258 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-176 | hs | 16 | 13 | 926,069 | 57,143 | 0.071 | 268 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-179 | hs | 25 | 17 | 618,403 | 30,842 | 0.040 | 148 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-187 | hs | 16 | 11 | 361,649 | 23,411 | 0.029 | 110 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-194 | hs | 20 | 15 | 651,843 | 41,033 | 0.047 | 185 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-195 | ts | 23 | 19 | 1,088,288 | 43,020 | 0.062 | 198 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-199 | ts | 33 | 28 | 2,279,743 | 74,009 | 0.222 | 348 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-202 | otel-demo | 17 | 17 | 659,206 | 31,488 | 0.041 | 149 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-203 | ts | 18 | 13 | 626,764 | 31,221 | 0.044 | 141 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-208 | ts | 18 | 15 | 835,300 | 51,605 | 0.061 | 224 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-212 | ts | 40 | 33 | 2,543,603 | 61,157 | 0.237 | 285 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-216 | ts | 24 | 18 | 760,659 | 42,721 | 0.054 | 183 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-226 | ts | 22 | 23 | 1,365,276 | 45,818 | 0.069 | 220 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-233 | hs | 21 | 19 | 715,226 | 33,619 | 0.043 | 161 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-235 | ts | 25 | 18 | 1,067,301 | 58,333 | 0.069 | 236 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-237 | ts | 24 | 17 | 857,816 | 29,779 | 0.049 | 136 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-240 | hs | 10 | 8 | 307,332 | 19,342 | 0.029 | 92 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-251 | ts | 16 | 12 | 484,980 | 29,846 | 0.038 | 148 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-255 | ts | 26 | 27 | 1,122,085 | 41,254 | 0.055 | 191 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-256 | ts | 21 | 14 | 747,879 | 33,739 | 0.048 | 160 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-258 | ts | 26 | 19 | 1,043,206 | 42,056 | 0.058 | 200 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-264 | hs | 11 | 9 | 405,579 | 21,636 | 0.031 | 104 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-265 | ts | 16 | 14 | 878,899 | 42,322 | 0.059 | 195 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-267 | ts | 14 | 13 | 642,300 | 29,641 | 0.042 | 139 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-270 | ts | 12 | 11 | 395,728 | 22,883 | 0.032 | 110 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-274 | ts | 19 | 17 | 868,245 | 46,996 | 0.061 | 193 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-284 | otel-demo | 20 | 17 | 708,208 | 38,825 | 0.049 | 171 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-287 | hs | 27 | 20 | 1,082,249 | 51,757 | 0.069 | 242 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-296 | ts | 18 | 15 | 681,993 | 40,231 | 0.052 | 176 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-300 | ts | 16 | 13 | 552,048 | 62,152 | 0.059 | 253 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-310 | ts | 15 | 16 | 728,192 | 34,392 | 0.045 | 162 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-311 | hs | 15 | 13 | 513,420 | 35,191 | 0.042 | 168 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-327 | ts | 24 | 25 | 1,463,694 | 54,206 | 0.075 | 256 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-329 | ts | 26 | 19 | 1,025,275 | 54,713 | 0.066 | 242 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-337 | hs | 20 | 15 | 581,728 | 32,437 | 0.039 | 153 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-339 | ts | 15 | 10 | 433,313 | 29,034 | 0.037 | 136 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-340 | ts | 13 | 11 | 687,289 | 48,582 | 0.054 | 194 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-352 | hs | 17 | 12 | 656,099 | 47,001 | 0.057 | 222 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-358 | ts | 19 | 14 | 746,456 | 41,178 | 0.053 | 177 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-359 | hs | 17 | 13 | 684,507 | 32,243 | 0.045 | 145 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-365 | ts | 15 | 12 | 710,572 | 55,959 | 0.061 | 224 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-384 | ts | 16 | 12 | 546,141 | 33,606 | 0.040 | 151 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-387 | ts | 23 | 20 | 1,224,438 | 49,799 | 0.066 | 230 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-389 | hs | 26 | 21 | 1,104,083 | 58,557 | 0.072 | 278 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-390 | hs | 16 | 14 | 489,174 | 26,548 | 0.035 | 125 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-391 | hs | 20 | 17 | 677,781 | 29,239 | 0.040 | 142 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-395 | ts | 20 | 12 | 530,439 | 31,651 | 0.041 | 144 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-398 | otel-demo | 16 | 11 | 369,170 | 27,643 | 0.032 | 126 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-401 | ts | 34 | 27 | 1,598,555 | 58,025 | 0.079 | 275 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-402 | hs | 16 | 11 | 378,128 | 21,820 | 0.030 | 105 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-403 | ts | 21 | 20 | 1,156,837 | 37,124 | 0.058 | 174 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-406 | ts | 19 | 15 | 831,776 | 43,625 | 0.054 | 203 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-414 | hs | 12 | 11 | 389,609 | 26,608 | 0.033 | 129 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-418 | ts | 40 | 39 | 3,634,182 | 115,602 | 0.369 | 510 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-426 | otel-demo | 20 | 17 | 632,445 | 34,797 | 0.044 | 168 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-431 | hs | 23 | 15 | 610,684 | 28,491 | 0.042 | 132 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-432 | hs | 17 | 14 | 511,993 | 24,685 | 0.034 | 119 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-433 | ts | 18 | 15 | 880,193 | 55,200 | 0.066 | 227 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-434 | hs | 24 | 21 | 718,329 | 31,241 | 0.041 | 156 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-435 | ts | 45 | 47 | 4,684,169 | 95,108 | 0.371 | 457 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-438 | ts | 18 | 13 | 583,842 | 27,683 | 0.039 | 130 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-442 | ts | 19 | 20 | 836,900 | 33,339 | 0.045 | 156 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-443 | ts | 24 | 26 | 1,245,872 | 57,645 | 0.071 | 259 | 1 | 1.00 | 1 | the model stopped calling tools |  |

Total: $6.36, 90,261,879 prompt tokens, 4,123,190 output tokens.
