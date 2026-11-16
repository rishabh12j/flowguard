# Baseline run: claude:claude-haiku-5-5, 100 development cases

| Score | Mean |
|---|---|
| f1 | 0.750 |
| precision | 0.748 |
| recall | 0.760 |
| acc | 0.720 |
| any_hit | 0.980 |
| all_hit | 0.960 |
| type_acc | 0.781 |
| node_f1 | 0.922 |
| edge_f1 | 0.858 |
| path_acc | 0.768 |
| path_acc_service | 0.979 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-011 | ts | 16 | 13 | 525,096 | 32,623 | 0.039 | 146 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-012 | hs | 20 | 17 | 416,121 | 20,950 | 0.027 | 96 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-021 | ts | 29 | 26 | 1,743,415 | 39,613 | 0.078 | 185 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-036 | hs | 31 | 28 | 1,023,075 | 30,842 | 0.046 | 152 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-038 | ts | 23 | 18 | 883,152 | 36,300 | 0.050 | 161 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-046 | hs | 13 | 13 | 358,447 | 19,355 | 0.025 | 90 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-056 | hs | 17 | 13 | 622,722 | 38,630 | 0.047 | 175 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-059 | otel-demo | 18 | 18 | 659,566 | 30,215 | 0.039 | 131 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-065 | hs | 17 | 12 | 355,907 | 21,993 | 0.027 | 100 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-073 | ts | 13 | 10 | 379,635 | 18,329 | 0.027 | 87 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-079 | hs | 22 | 17 | 572,390 | 26,765 | 0.035 | 123 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-080 | ts | 10 | 7 | 266,851 | 15,591 | 0.023 | 74 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-083 | hs | 21 | 15 | 436,417 | 20,420 | 0.028 | 94 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-084 | ts | 16 | 13 | 695,620 | 34,859 | 0.045 | 146 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-086 | hs | 18 | 10 | 326,794 | 19,015 | 0.024 | 85 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-089 | hs | 15 | 14 | 455,568 | 19,101 | 0.029 | 88 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-092 | ts | 35 | 22 | 1,197,780 | 36,820 | 0.055 | 175 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-093 | hs | 16 | 12 | 319,078 | 18,391 | 0.024 | 85 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-095 | ts | 26 | 22 | 872,968 | 23,453 | 0.038 | 112 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-103 | hs | 23 | 18 | 712,813 | 32,260 | 0.043 | 151 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-106 | ts | 36 | 25 | 1,421,293 | 38,333 | 0.060 | 178 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-117 | ts | 48 | 36 | 1,866,121 | 47,579 | 0.067 | 216 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-120 | ts | 33 | 33 | 1,660,291 | 41,087 | 0.062 | 198 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-123 | ts | 18 | 15 | 716,342 | 24,187 | 0.039 | 117 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-124 | ts | 27 | 18 | 967,298 | 32,654 | 0.053 | 138 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-125 | ts | 21 | 16 | 723,013 | 32,334 | 0.042 | 136 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-126 | hs | 22 | 15 | 455,096 | 21,333 | 0.028 | 102 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-129 | ts | 19 | 15 | 709,034 | 28,422 | 0.040 | 126 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-134 | ts | 15 | 13 | 450,638 | 19,688 | 0.030 | 88 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-146 | ts | 22 | 15 | 784,445 | 33,431 | 0.049 | 149 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-151 | ts | 21 | 15 | 723,904 | 36,378 | 0.046 | 161 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-154 | ts | 23 | 17 | 729,859 | 31,882 | 0.043 | 134 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-155 | otel-demo | 22 | 18 | 701,554 | 39,366 | 0.048 | 184 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-164 | hs | 16 | 10 | 403,333 | 21,282 | 0.033 | 99 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-165 | ts | 24 | 21 | 1,151,968 | 42,704 | 0.058 | 205 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-170 | ts | 29 | 27 | 1,624,512 | 42,741 | 0.066 | 197 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-171 | otel-demo | 32 | 22 | 1,255,759 | 49,017 | 0.068 | 224 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-172 | ts | 19 | 12 | 507,793 | 27,642 | 0.038 | 116 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-176 | hs | 14 | 11 | 305,370 | 18,453 | 0.025 | 83 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-179 | hs | 19 | 14 | 894,297 | 40,078 | 0.052 | 184 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-187 | hs | 19 | 13 | 427,393 | 22,030 | 0.030 | 99 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-194 | hs | 18 | 17 | 602,194 | 31,899 | 0.038 | 147 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-195 | ts | 18 | 13 | 943,998 | 43,676 | 0.062 | 193 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-199 | ts | 34 | 29 | 1,922,291 | 49,733 | 0.145 | 235 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-202 | otel-demo | 16 | 13 | 611,847 | 33,291 | 0.044 | 157 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-203 | ts | 15 | 12 | 510,010 | 22,916 | 0.030 | 104 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-208 | ts | 19 | 15 | 641,010 | 35,473 | 0.045 | 150 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-212 | ts | 33 | 26 | 1,429,099 | 31,123 | 0.055 | 156 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-216 | ts | 13 | 11 | 429,051 | 28,517 | 0.036 | 124 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-226 | ts | 22 | 21 | 787,910 | 35,049 | 0.045 | 162 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-233 | hs | 16 | 16 | 494,620 | 25,698 | 0.032 | 120 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-235 | ts | 16 | 16 | 673,714 | 33,064 | 0.042 | 148 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-237 | ts | 23 | 16 | 761,429 | 25,866 | 0.039 | 115 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-240 | hs | 15 | 11 | 468,359 | 23,792 | 0.036 | 110 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-251 | ts | 11 | 8 | 326,913 | 18,290 | 0.025 | 86 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-255 | ts | 26 | 27 | 1,057,091 | 33,719 | 0.047 | 162 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-256 | ts | 19 | 16 | 824,550 | 30,245 | 0.045 | 150 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-258 | ts | 33 | 23 | 1,662,412 | 60,614 | 0.085 | 278 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-264 | hs | 17 | 14 | 456,393 | 23,440 | 0.030 | 105 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-265 | ts | 21 | 16 | 876,050 | 24,269 | 0.045 | 116 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-267 | ts | 22 | 17 | 731,751 | 29,012 | 0.039 | 136 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-270 | ts | 9 | 7 | 210,949 | 12,255 | 0.019 | 58 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-274 | ts | 18 | 15 | 732,971 | 33,733 | 0.045 | 141 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-284 | otel-demo | 20 | 17 | 708,929 | 26,790 | 0.043 | 123 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-287 | hs | 16 | 14 | 708,079 | 34,255 | 0.047 | 155 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-296 | ts | 20 | 19 | 846,306 | 36,238 | 0.048 | 156 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-300 | ts | 20 | 14 | 877,619 | 36,228 | 0.048 | 160 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-310 | ts | 25 | 16 | 681,214 | 28,486 | 0.038 | 128 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-311 | hs | 24 | 16 | 545,939 | 26,327 | 0.034 | 128 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-327 | ts | 38 | 35 | 1,910,784 | 41,511 | 0.067 | 198 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-329 | ts | 19 | 13 | 512,822 | 30,130 | 0.037 | 133 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-337 | hs | 21 | 17 | 653,986 | 32,344 | 0.039 | 173 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-339 | ts | 25 | 22 | 1,327,470 | 39,644 | 0.063 | 191 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-340 | ts | 13 | 11 | 480,181 | 37,197 | 0.040 | 149 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-352 | hs | 27 | 16 | 815,820 | 41,892 | 0.053 | 187 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-358 | ts | 21 | 15 | 953,321 | 32,952 | 0.050 | 151 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-359 | hs | 17 | 14 | 450,508 | 19,209 | 0.028 | 89 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-365 | ts | 14 | 14 | 809,374 | 35,925 | 0.050 | 159 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-384 | ts | 18 | 13 | 518,856 | 19,570 | 0.034 | 91 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-387 | ts | 21 | 16 | 794,431 | 38,321 | 0.048 | 168 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-389 | hs | 21 | 19 | 898,020 | 39,844 | 0.052 | 182 | 0 | 0.50 | 1 | the model stopped calling tools |  |
| case-390 | hs | 16 | 13 | 494,778 | 21,413 | 0.030 | 106 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-391 | hs | 14 | 15 | 472,142 | 27,991 | 0.033 | 136 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-395 | ts | 15 | 10 | 393,510 | 22,493 | 0.029 | 105 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-398 | otel-demo | 17 | 12 | 538,701 | 23,355 | 0.034 | 110 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-401 | ts | 40 | 41 | 2,312,327 | 38,938 | 0.069 | 200 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-402 | hs | 22 | 14 | 473,359 | 20,314 | 0.030 | 94 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-403 | ts | 25 | 19 | 1,186,856 | 36,343 | 0.057 | 169 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-406 | ts | 15 | 13 | 630,610 | 29,221 | 0.040 | 131 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-414 | hs | 17 | 12 | 373,455 | 24,854 | 0.029 | 121 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-418 | ts | 49 | 51 | 4,031,829 | 58,912 | 0.331 | 284 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-426 | otel-demo | 22 | 20 | 958,045 | 28,830 | 0.047 | 136 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-431 | hs | 30 | 20 | 577,884 | 21,233 | 0.033 | 103 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-432 | hs | 22 | 14 | 408,734 | 19,185 | 0.027 | 93 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-433 | ts | 48 | 32 | 1,805,259 | 54,116 | 0.089 | 246 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-434 | hs | 14 | 12 | 528,677 | 24,706 | 0.033 | 116 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-435 | ts | 40 | 35 | 3,344,016 | 103,829 | 0.307 | 492 | 0 | 0.50 | 1 | the model stopped calling tools |  |
| case-438 | ts | 35 | 25 | 1,556,384 | 39,785 | 0.063 | 180 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-442 | ts | 39 | 25 | 1,791,326 | 45,308 | 0.179 | 217 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-443 | ts | 38 | 37 | 1,812,601 | 50,756 | 0.070 | 238 | 0 | 0.00 | 1 | the model stopped calling tools |  |

Total: $5.10, 86,641,492 prompt tokens, 3,200,265 output tokens.
