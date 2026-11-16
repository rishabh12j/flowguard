# Baseline run: claude:claude-haiku-5-5, 100 development cases

| Score | Mean |
|---|---|
| f1 | 0.730 |
| precision | 0.730 |
| recall | 0.735 |
| acc | 0.710 |
| any_hit | 0.980 |
| all_hit | 0.960 |
| type_acc | 0.755 |
| node_f1 | 0.918 |
| edge_f1 | 0.858 |
| path_acc | 0.737 |
| path_acc_service | 0.979 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-011 | ts | 10 | 9 | 434,746 | 25,748 | 0.034 | 117 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-012 | hs | 16 | 12 | 345,617 | 17,406 | 0.025 | 85 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-021 | ts | 35 | 27 | 1,805,016 | 38,731 | 0.146 | 186 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-036 | hs | 28 | 23 | 1,419,379 | 32,730 | 0.124 | 158 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-038 | ts | 19 | 20 | 928,110 | 28,331 | 0.045 | 141 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-046 | hs | 22 | 16 | 608,207 | 22,240 | 0.033 | 108 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-056 | hs | 12 | 10 | 267,083 | 17,912 | 0.024 | 91 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-059 | otel-demo | 19 | 12 | 423,734 | 21,470 | 0.031 | 101 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-065 | hs | 15 | 13 | 502,839 | 22,224 | 0.029 | 107 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-073 | ts | 15 | 14 | 444,740 | 21,268 | 0.028 | 103 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-079 | hs | 22 | 15 | 574,927 | 24,367 | 0.036 | 115 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-080 | ts | 11 | 8 | 288,562 | 14,860 | 0.023 | 71 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-083 | hs | 11 | 8 | 243,949 | 14,565 | 0.021 | 71 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-084 | ts | 12 | 10 | 439,369 | 29,742 | 0.038 | 136 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-086 | hs | 25 | 15 | 494,589 | 22,249 | 0.032 | 102 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-089 | hs | 22 | 14 | 424,069 | 17,973 | 0.027 | 91 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-092 | ts | 26 | 16 | 645,534 | 30,141 | 0.041 | 139 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-093 | hs | 22 | 14 | 409,102 | 18,094 | 0.026 | 87 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-095 | ts | 17 | 14 | 763,393 | 25,261 | 0.041 | 120 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-103 | hs | 30 | 29 | 1,539,401 | 43,344 | 0.063 | 213 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-106 | ts | 31 | 22 | 1,165,306 | 39,573 | 0.055 | 179 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-117 | ts | 30 | 26 | 1,096,898 | 33,262 | 0.049 | 158 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-120 | ts | 32 | 28 | 1,609,125 | 45,876 | 0.068 | 218 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-123 | ts | 17 | 11 | 424,176 | 25,125 | 0.032 | 120 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-124 | ts | 27 | 20 | 964,345 | 33,911 | 0.051 | 153 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-125 | ts | 12 | 13 | 538,617 | 26,042 | 0.036 | 118 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-126 | hs | 15 | 12 | 285,935 | 20,511 | 0.024 | 98 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-129 | ts | 16 | 14 | 747,162 | 27,077 | 0.044 | 129 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-134 | ts | 11 | 9 | 348,929 | 16,462 | 0.025 | 82 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-146 | ts | 15 | 11 | 422,483 | 28,042 | 0.033 | 128 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-151 | ts | 17 | 15 | 526,163 | 23,958 | 0.032 | 119 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-154 | ts | 20 | 17 | 736,769 | 34,189 | 0.045 | 146 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-155 | otel-demo | 24 | 18 | 1,024,487 | 47,051 | 0.062 | 222 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-164 | hs | 14 | 11 | 385,834 | 18,974 | 0.028 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-165 | ts | 22 | 15 | 618,454 | 26,386 | 0.038 | 124 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-170 | ts | 22 | 21 | 859,271 | 41,865 | 0.052 | 196 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-171 | otel-demo | 27 | 22 | 1,041,083 | 26,082 | 0.046 | 126 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-172 | ts | 25 | 20 | 1,261,963 | 43,648 | 0.063 | 192 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-176 | hs | 26 | 22 | 860,219 | 36,717 | 0.050 | 386 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-179 | hs | 16 | 11 | 329,954 | 19,010 | 0.026 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-187 | hs | 16 | 11 | 342,498 | 20,448 | 0.026 | 95 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-194 | hs | 20 | 16 | 519,209 | 28,947 | 0.034 | 141 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-195 | ts | 24 | 20 | 937,700 | 28,515 | 0.045 | 136 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-199 | ts | 22 | 20 | 1,050,719 | 28,438 | 0.049 | 143 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-202 | otel-demo | 18 | 14 | 600,157 | 24,214 | 0.035 | 114 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-203 | ts | 13 | 10 | 279,213 | 17,454 | 0.024 | 84 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-208 | ts | 10 | 11 | 526,899 | 29,858 | 0.040 | 139 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-212 | ts | 30 | 21 | 1,350,399 | 35,368 | 0.058 | 175 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-216 | ts | 22 | 16 | 793,617 | 31,305 | 0.046 | 144 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-226 | ts | 18 | 17 | 772,537 | 27,017 | 0.040 | 130 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-233 | hs | 21 | 19 | 792,440 | 30,626 | 0.041 | 142 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-235 | ts | 24 | 23 | 947,952 | 33,539 | 0.046 | 154 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-237 | ts | 19 | 11 | 360,100 | 20,813 | 0.029 | 96 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-240 | hs | 12 | 13 | 456,496 | 20,434 | 0.028 | 100 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-251 | ts | 28 | 20 | 774,276 | 28,722 | 0.040 | 143 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-255 | ts | 22 | 23 | 940,706 | 27,723 | 0.042 | 132 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-256 | ts | 24 | 15 | 519,651 | 22,977 | 0.031 | 110 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-258 | ts | 31 | 21 | 853,472 | 32,376 | 0.044 | 157 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-264 | hs | 17 | 14 | 459,315 | 16,366 | 0.026 | 84 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-265 | ts | 18 | 13 | 704,800 | 21,816 | 0.040 | 109 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-267 | ts | 18 | 16 | 685,905 | 24,982 | 0.038 | 119 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-270 | ts | 18 | 13 | 425,964 | 17,751 | 0.028 | 86 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-274 | ts | 15 | 12 | 640,831 | 33,325 | 0.048 | 140 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-284 | otel-demo | 18 | 13 | 447,791 | 26,160 | 0.033 | 122 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-287 | hs | 22 | 20 | 907,544 | 37,891 | 0.054 | 178 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-296 | ts | 17 | 14 | 603,294 | 31,638 | 0.042 | 144 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-300 | ts | 21 | 16 | 792,439 | 34,039 | 0.047 | 152 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-310 | ts | 18 | 15 | 518,725 | 19,265 | 0.031 | 95 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-311 | hs | 16 | 16 | 626,525 | 26,603 | 0.037 | 128 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-327 | ts | 37 | 33 | 2,540,778 | 46,922 | 0.178 | 219 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-329 | ts | 18 | 13 | 749,196 | 31,196 | 0.044 | 138 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-337 | hs | 15 | 12 | 366,973 | 18,654 | 0.028 | 90 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-339 | ts | 25 | 19 | 1,498,007 | 37,667 | 0.068 | 179 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-340 | ts | 14 | 11 | 462,094 | 25,225 | 0.035 | 112 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-352 | hs | 23 | 16 | 670,243 | 32,233 | 0.045 | 147 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-358 | ts | 15 | 11 | 622,154 | 26,498 | 0.041 | 119 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-359 | hs | 18 | 13 | 458,226 | 22,275 | 0.030 | 105 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-365 | ts | 18 | 15 | 733,633 | 37,971 | 0.050 | 174 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-384 | ts | 12 | 9 | 248,638 | 13,626 | 0.021 | 63 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-387 | ts | 21 | 16 | 725,896 | 27,597 | 0.040 | 128 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-389 | hs | 20 | 15 | 746,935 | 43,687 | 0.056 | 200 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-390 | hs | 13 | 12 | 364,662 | 19,159 | 0.027 | 89 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-391 | hs | 23 | 16 | 482,346 | 20,514 | 0.028 | 97 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-395 | ts | 26 | 20 | 1,084,943 | 31,637 | 0.053 | 153 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-398 | otel-demo | 16 | 16 | 545,731 | 23,698 | 0.034 | 114 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-401 | ts | 30 | 21 | 1,435,545 | 33,678 | 0.157 | 161 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-402 | hs | 17 | 13 | 427,533 | 19,677 | 0.026 | 95 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-403 | ts | 23 | 23 | 1,402,220 | 38,316 | 0.063 | 186 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-406 | ts | 20 | 13 | 523,613 | 30,484 | 0.035 | 140 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-414 | hs | 12 | 8 | 184,984 | 16,657 | 0.020 | 78 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-418 | ts | 40 | 41 | 3,610,859 | 76,888 | 0.342 | 358 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-426 | otel-demo | 16 | 15 | 564,024 | 25,497 | 0.036 | 119 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-431 | hs | 26 | 16 | 494,078 | 21,280 | 0.032 | 101 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-432 | hs | 27 | 21 | 605,471 | 22,952 | 0.033 | 117 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-433 | ts | 36 | 27 | 1,865,321 | 42,591 | 0.184 | 205 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-434 | hs | 12 | 11 | 364,222 | 21,644 | 0.028 | 105 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-435 | ts | 25 | 21 | 1,723,927 | 54,832 | 0.153 | 259 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-438 | ts | 28 | 18 | 928,011 | 26,060 | 0.044 | 123 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-442 | ts | 16 | 13 | 508,662 | 21,305 | 0.032 | 98 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-443 | ts | 20 | 16 | 831,257 | 37,752 | 0.050 | 170 | 0 | 0.00 | 1 | the model stopped calling tools |  |

Total: $4.86, 75,650,895 prompt tokens, 2,829,199 output tokens.
