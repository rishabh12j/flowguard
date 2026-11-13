# Baseline run: claude:claude-haiku-5-5, 100 development cases

| Score | Mean |
|---|---|
| f1 | 0.663 |
| precision | 0.655 |
| recall | 0.680 |
| acc | 0.620 |
| any_hit | 0.980 |
| all_hit | 0.980 |
| type_acc | 0.694 |
| node_f1 | 0.943 |
| edge_f1 | 0.891 |
| path_acc | 0.684 |
| path_acc_service | 0.989 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-011 | ts | 23 | 13 | 444,522 | 16,436 | 0.026 | 69 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-012 | hs | 20 | 17 | 427,501 | 12,035 | 0.021 | 56 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-021 | ts | 56 | 36 | 2,477,566 | 50,120 | 0.219 | 218 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-036 | hs | 21 | 19 | 599,679 | 15,552 | 0.026 | 78 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-038 | ts | 43 | 29 | 1,296,964 | 27,501 | 0.047 | 125 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-046 | hs | 20 | 13 | 252,887 | 12,035 | 0.016 | 53 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-056 | hs | 21 | 14 | 274,918 | 16,182 | 0.019 | 71 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-059 | otel-demo | 21 | 14 | 437,809 | 13,846 | 0.024 | 59 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-065 | hs | 18 | 14 | 322,101 | 10,443 | 0.017 | 47 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-073 | ts | 16 | 12 | 314,942 | 10,432 | 0.018 | 49 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-079 | hs | 20 | 14 | 349,167 | 11,393 | 0.019 | 51 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-080 | ts | 16 | 11 | 239,586 | 9,189 | 0.015 | 41 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-083 | hs | 14 | 10 | 187,028 | 8,494 | 0.014 | 40 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-084 | ts | 14 | 12 | 268,257 | 14,931 | 0.018 | 62 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-086 | hs | 20 | 15 | 273,542 | 9,616 | 0.014 | 44 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-089 | hs | 18 | 13 | 303,902 | 8,601 | 0.016 | 41 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-092 | ts | 30 | 21 | 803,935 | 18,467 | 0.032 | 88 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-093 | hs | 14 | 9 | 159,814 | 7,598 | 0.011 | 33 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-095 | ts | 27 | 22 | 929,849 | 16,283 | 0.033 | 79 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-103 | hs | 25 | 23 | 742,195 | 19,896 | 0.032 | 92 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-106 | ts | 40 | 27 | 1,115,168 | 33,498 | 0.046 | 150 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-117 | ts | 27 | 17 | 533,164 | 15,223 | 0.024 | 68 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-120 | ts | 32 | 31 | 1,528,229 | 29,338 | 0.050 | 140 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-123 | ts | 15 | 10 | 231,723 | 9,485 | 0.015 | 45 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-124 | ts | 22 | 14 | 471,511 | 18,377 | 0.027 | 77 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-125 | ts | 14 | 12 | 271,215 | 13,518 | 0.017 | 58 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-126 | hs | 24 | 14 | 289,568 | 12,438 | 0.017 | 64 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-129 | ts | 16 | 13 | 343,191 | 14,000 | 0.020 | 65 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-134 | ts | 11 | 11 | 257,362 | 7,600 | 0.014 | 34 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-146 | ts | 18 | 13 | 395,878 | 17,085 | 0.024 | 70 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-151 | ts | 26 | 19 | 672,303 | 17,007 | 0.028 | 79 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-154 | ts | 19 | 17 | 681,493 | 17,984 | 0.030 | 84 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-155 | otel-demo | 26 | 24 | 943,606 | 32,877 | 0.044 | 147 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-164 | hs | 23 | 15 | 426,591 | 11,973 | 0.021 | 56 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-165 | ts | 28 | 17 | 479,710 | 17,878 | 0.024 | 82 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-170 | ts | 24 | 20 | 915,331 | 20,081 | 0.037 | 92 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-171 | otel-demo | 29 | 19 | 742,056 | 18,136 | 0.032 | 82 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-172 | ts | 18 | 16 | 594,220 | 26,563 | 0.034 | 107 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-176 | hs | 22 | 16 | 291,500 | 12,328 | 0.016 | 57 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-179 | hs | 21 | 13 | 363,121 | 16,710 | 0.024 | 72 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-187 | hs | 20 | 14 | 285,842 | 10,006 | 0.016 | 48 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-194 | hs | 26 | 23 | 716,044 | 20,808 | 0.031 | 100 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-195 | ts | 27 | 19 | 836,209 | 24,817 | 0.040 | 109 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-199 | ts | 28 | 23 | 745,696 | 17,311 | 0.030 | 84 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-202 | otel-demo | 20 | 16 | 470,644 | 14,633 | 0.024 | 67 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-203 | ts | 23 | 16 | 621,224 | 14,160 | 0.027 | 63 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-208 | ts | 15 | 13 | 544,928 | 18,402 | 0.030 | 80 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-212 | ts | 39 | 26 | 1,271,034 | 27,852 | 0.047 | 132 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-216 | ts | 21 | 15 | 337,241 | 15,161 | 0.019 | 66 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-226 | ts | 27 | 26 | 1,156,224 | 22,034 | 0.039 | 100 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-233 | hs | 14 | 10 | 185,335 | 8,861 | 0.013 | 39 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-235 | ts | 17 | 14 | 472,297 | 16,695 | 0.025 | 67 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-237 | ts | 15 | 13 | 419,314 | 11,970 | 0.022 | 54 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-240 | hs | 10 | 10 | 188,051 | 8,253 | 0.013 | 39 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-251 | ts | 11 | 9 | 203,985 | 8,895 | 0.014 | 39 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-255 | ts | 26 | 19 | 735,935 | 25,550 | 0.036 | 114 | 0 | 0.50 | 1 | the model stopped calling tools |  |
| case-256 | ts | 15 | 10 | 293,183 | 10,040 | 0.020 | 45 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-258 | ts | 29 | 24 | 994,089 | 18,921 | 0.035 | 95 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-264 | hs | 26 | 12 | 212,774 | 11,183 | 0.014 | 50 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-265 | ts | 25 | 20 | 813,355 | 16,554 | 0.030 | 77 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-267 | ts | 22 | 15 | 542,023 | 22,167 | 0.031 | 98 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-270 | ts | 28 | 16 | 415,559 | 15,330 | 0.022 | 74 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-274 | ts | 17 | 12 | 301,957 | 17,691 | 0.021 | 71 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-284 | otel-demo | 20 | 13 | 284,098 | 12,845 | 0.017 | 55 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-287 | hs | 16 | 12 | 270,042 | 12,676 | 0.018 | 56 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-296 | ts | 23 | 17 | 604,941 | 19,470 | 0.030 | 85 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-300 | ts | 28 | 28 | 1,119,408 | 25,142 | 0.039 | 121 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-310 | ts | 14 | 13 | 350,853 | 10,786 | 0.019 | 50 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-311 | hs | 24 | 15 | 386,488 | 16,582 | 0.022 | 76 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-327 | ts | 40 | 29 | 1,939,198 | 35,875 | 0.176 | 168 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-329 | ts | 24 | 16 | 521,287 | 20,680 | 0.028 | 91 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-337 | hs | 20 | 17 | 357,531 | 14,659 | 0.019 | 68 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-339 | ts | 34 | 28 | 1,356,880 | 25,668 | 0.048 | 124 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-340 | ts | 13 | 9 | 256,765 | 14,922 | 0.020 | 59 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-352 | hs | 18 | 14 | 300,076 | 11,068 | 0.018 | 50 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-358 | ts | 24 | 14 | 348,384 | 16,071 | 0.021 | 72 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-359 | hs | 16 | 11 | 225,756 | 10,410 | 0.015 | 48 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-365 | ts | 15 | 13 | 411,069 | 15,832 | 0.024 | 70 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-384 | ts | 12 | 10 | 219,519 | 8,628 | 0.014 | 40 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-387 | ts | 31 | 21 | 791,736 | 24,142 | 0.034 | 104 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-389 | hs | 28 | 22 | 545,407 | 19,982 | 0.025 | 90 | 0 | 0.50 | 1 | the model stopped calling tools |  |
| case-390 | hs | 15 | 11 | 243,900 | 9,680 | 0.015 | 42 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-391 | hs | 25 | 21 | 670,555 | 20,387 | 0.029 | 94 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-395 | ts | 17 | 11 | 299,543 | 11,721 | 0.019 | 52 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-398 | otel-demo | 26 | 15 | 525,819 | 19,005 | 0.029 | 82 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-401 | ts | 30 | 24 | 1,455,464 | 28,238 | 0.141 | 130 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-402 | hs | 19 | 15 | 370,213 | 11,371 | 0.019 | 54 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-403 | ts | 27 | 21 | 858,557 | 16,468 | 0.034 | 75 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-406 | ts | 26 | 21 | 815,109 | 26,198 | 0.037 | 121 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-414 | hs | 14 | 11 | 273,170 | 10,478 | 0.017 | 50 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-418 | ts | 35 | 36 | 2,577,000 | 47,726 | 0.238 | 236 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-426 | otel-demo | 16 | 17 | 443,616 | 12,961 | 0.022 | 60 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-431 | hs | 25 | 16 | 443,579 | 12,310 | 0.023 | 63 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-432 | hs | 16 | 13 | 287,883 | 9,925 | 0.016 | 48 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-433 | ts | 40 | 41 | 2,482,562 | 46,003 | 0.202 | 216 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-434 | hs | 20 | 13 | 308,906 | 11,197 | 0.017 | 49 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-435 | ts | 26 | 24 | 1,290,678 | 28,134 | 0.049 | 132 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-438 | ts | 24 | 16 | 560,800 | 14,008 | 0.024 | 62 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-442 | ts | 28 | 19 | 1,254,469 | 19,501 | 0.100 | 90 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-443 | ts | 45 | 36 | 2,074,996 | 31,093 | 0.058 | 144 | 1 | 1.00 | 1 | the model stopped calling tools |  |

Total: $3.46, 62,942,304 prompt tokens, 1,750,285 output tokens.
