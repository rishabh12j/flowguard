# Baseline run: claude:claude-haiku-5-5, 100 development cases

| Score | Mean |
|---|---|
| f1 | 0.580 |
| precision | 0.575 |
| recall | 0.590 |
| acc | 0.560 |
| any_hit | 0.910 |
| all_hit | 0.900 |
| type_acc | 0.648 |
| node_f1 | 0.898 |
| edge_f1 | 0.827 |
| path_acc | 0.579 |
| path_acc_service | 0.895 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-011 | ts | 24 | 16 | 474,376 | 13,984 | 0.024 | 66 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-012 | hs | 24 | 14 | 336,510 | 10,344 | 0.017 | 50 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-021 | ts | 32 | 18 | 613,473 | 17,703 | 0.030 | 82 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-036 | hs | 34 | 19 | 815,018 | 16,295 | 0.035 | 77 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-038 | ts | 33 | 17 | 471,357 | 17,180 | 0.024 | 77 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-046 | hs | 19 | 11 | 244,180 | 9,387 | 0.015 | 43 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-056 | hs | 33 | 19 | 489,577 | 15,776 | 0.023 | 77 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-059 | otel-demo | 24 | 14 | 310,182 | 13,534 | 0.019 | 62 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-065 | hs | 24 | 20 | 639,527 | 14,412 | 0.025 | 70 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-073 | ts | 20 | 13 | 311,230 | 10,491 | 0.019 | 51 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-079 | hs | 25 | 13 | 393,572 | 10,952 | 0.021 | 50 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-080 | ts | 20 | 13 | 291,368 | 10,248 | 0.018 | 50 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-083 | hs | 19 | 10 | 244,684 | 8,854 | 0.017 | 42 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-084 | ts | 34 | 29 | 1,175,356 | 23,549 | 0.040 | 109 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-086 | hs | 24 | 12 | 338,563 | 12,993 | 0.021 | 57 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-089 | hs | 21 | 11 | 286,218 | 8,427 | 0.018 | 40 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-092 | ts | 32 | 21 | 879,248 | 17,482 | 0.033 | 81 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-093 | hs | 18 | 12 | 205,378 | 7,964 | 0.012 | 37 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-095 | ts | 24 | 23 | 834,265 | 14,982 | 0.031 | 77 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-103 | hs | 30 | 19 | 546,465 | 16,390 | 0.025 | 83 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-106 | ts | 58 | 37 | 2,810,645 | 41,195 | 0.243 | 204 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-117 | ts | 42 | 20 | 811,200 | 20,863 | 0.037 | 96 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-120 | ts | 33 | 18 | 725,690 | 22,325 | 0.034 | 106 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-123 | ts | 16 | 12 | 249,778 | 8,137 | 0.015 | 44 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-124 | ts | 31 | 17 | 541,150 | 15,124 | 0.026 | 76 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-125 | ts | 18 | 12 | 239,327 | 12,432 | 0.017 | 56 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-126 | hs | 30 | 16 | 306,452 | 13,278 | 0.018 | 67 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-129 | ts | 24 | 15 | 438,977 | 13,619 | 0.022 | 65 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-134 | ts | 29 | 14 | 491,139 | 13,156 | 0.025 | 64 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-146 | ts | 30 | 16 | 547,285 | 16,321 | 0.028 | 78 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-151 | ts | 37 | 22 | 1,008,485 | 22,368 | 0.040 | 110 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-154 | ts | 33 | 21 | 606,384 | 23,955 | 0.031 | 111 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-155 | otel-demo | 37 | 20 | 570,649 | 17,565 | 0.028 | 81 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-164 | hs | 25 | 13 | 269,965 | 8,044 | 0.015 | 44 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-165 | ts | 48 | 25 | 1,223,302 | 29,798 | 0.047 | 138 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-170 | ts | 36 | 22 | 828,387 | 18,631 | 0.032 | 93 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-171 | otel-demo | 30 | 15 | 365,426 | 13,913 | 0.021 | 67 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-172 | ts | 38 | 19 | 759,456 | 22,753 | 0.036 | 104 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-176 | hs | 27 | 14 | 327,732 | 11,286 | 0.018 | 54 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-179 | hs | 25 | 15 | 401,982 | 10,433 | 0.019 | 54 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-187 | hs | 22 | 13 | 323,136 | 9,244 | 0.018 | 48 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-194 | hs | 40 | 20 | 774,080 | 21,737 | 0.034 | 110 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-195 | ts | 36 | 17 | 714,943 | 22,394 | 0.036 | 103 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-199 | ts | 38 | 21 | 911,936 | 21,995 | 0.037 | 112 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-202 | otel-demo | 40 | 19 | 820,301 | 19,525 | 0.035 | 94 | 0 | 0.67 | 1 | the model stopped calling tools |  |
| case-203 | ts | 37 | 17 | 560,421 | 16,423 | 0.027 | 78 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-208 | ts | 29 | 18 | 609,519 | 15,910 | 0.026 | 78 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-212 | ts | 35 | 17 | 659,475 | 20,906 | 0.033 | 97 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-216 | ts | 27 | 15 | 392,179 | 13,319 | 0.022 | 62 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-226 | ts | 43 | 24 | 920,831 | 23,139 | 0.037 | 115 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-233 | hs | 27 | 19 | 610,591 | 14,428 | 0.025 | 78 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-235 | ts | 45 | 30 | 1,581,486 | 28,125 | 0.050 | 139 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-237 | ts | 27 | 18 | 617,444 | 14,357 | 0.026 | 68 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-240 | hs | 26 | 15 | 388,071 | 11,219 | 0.019 | 56 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-251 | ts | 17 | 13 | 302,959 | 9,864 | 0.017 | 50 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-255 | ts | 47 | 31 | 1,605,439 | 29,752 | 0.051 | 149 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-256 | ts | 31 | 16 | 405,331 | 15,295 | 0.022 | 76 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-258 | ts | 44 | 25 | 1,328,419 | 25,129 | 0.046 | 124 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-264 | hs | 27 | 16 | 389,188 | 11,601 | 0.019 | 57 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-265 | ts | 37 | 17 | 466,041 | 15,767 | 0.023 | 76 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-267 | ts | 46 | 28 | 1,277,629 | 31,211 | 0.047 | 152 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-270 | ts | 38 | 18 | 608,687 | 18,725 | 0.028 | 92 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-274 | ts | 18 | 12 | 283,755 | 14,305 | 0.020 | 61 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-284 | otel-demo | 21 | 12 | 264,870 | 11,897 | 0.017 | 55 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-287 | hs | 17 | 9 | 193,021 | 7,545 | 0.015 | 41 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-296 | ts | 21 | 13 | 364,227 | 13,191 | 0.022 | 63 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-300 | ts | 38 | 21 | 777,165 | 26,631 | 0.037 | 123 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-310 | ts | 37 | 18 | 721,334 | 19,846 | 0.034 | 98 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-311 | hs | 21 | 17 | 437,833 | 12,314 | 0.021 | 66 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-327 | ts | 47 | 30 | 1,377,335 | 27,754 | 0.047 | 136 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-329 | ts | 30 | 18 | 646,148 | 18,394 | 0.032 | 90 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-337 | hs | 31 | 17 | 530,285 | 18,644 | 0.026 | 90 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-339 | ts | 33 | 26 | 1,073,799 | 20,489 | 0.038 | 107 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-340 | ts | 29 | 15 | 452,598 | 16,570 | 0.025 | 78 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-352 | hs | 28 | 14 | 470,835 | 12,284 | 0.025 | 65 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-358 | ts | 30 | 15 | 444,142 | 16,066 | 0.025 | 77 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-359 | hs | 26 | 13 | 406,286 | 12,630 | 0.021 | 63 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-365 | ts | 37 | 21 | 852,410 | 21,495 | 0.036 | 100 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-384 | ts | 26 | 15 | 411,709 | 11,564 | 0.020 | 58 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-387 | ts | 32 | 17 | 551,535 | 18,424 | 0.030 | 88 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-389 | hs | 29 | 18 | 635,141 | 16,060 | 0.027 | 81 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-390 | hs | 22 | 12 | 338,988 | 10,554 | 0.020 | 52 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-391 | hs | 32 | 21 | 661,570 | 16,007 | 0.028 | 84 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-395 | ts | 39 | 26 | 1,272,832 | 29,334 | 0.048 | 138 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-398 | otel-demo | 27 | 21 | 482,836 | 14,579 | 0.022 | 74 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-401 | ts | 43 | 33 | 1,614,022 | 21,597 | 0.047 | 117 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-402 | hs | 21 | 12 | 337,758 | 8,506 | 0.018 | 44 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-403 | ts | 31 | 16 | 549,506 | 16,576 | 0.028 | 81 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-406 | ts | 35 | 15 | 512,391 | 18,381 | 0.027 | 84 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-414 | hs | 19 | 20 | 546,453 | 12,250 | 0.024 | 68 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-418 | ts | 47 | 27 | 1,273,060 | 26,292 | 0.046 | 133 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-426 | otel-demo | 27 | 16 | 332,343 | 12,596 | 0.017 | 63 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-431 | hs | 23 | 12 | 253,580 | 9,479 | 0.016 | 46 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-432 | hs | 23 | 14 | 368,745 | 10,213 | 0.020 | 51 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-433 | ts | 42 | 25 | 1,084,933 | 24,147 | 0.041 | 112 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-434 | hs | 30 | 22 | 594,255 | 16,391 | 0.025 | 86 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-435 | ts | 36 | 16 | 498,298 | 15,612 | 0.027 | 75 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-438 | ts | 32 | 22 | 678,917 | 15,298 | 0.027 | 81 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-442 | ts | 49 | 26 | 1,210,116 | 31,715 | 0.047 | 149 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-443 | ts | 33 | 16 | 584,480 | 18,394 | 0.029 | 82 | 0 | 0.67 | 1 | the model stopped calling tools |  |

Total: $2.97, 63,781,575 prompt tokens, 1,680,232 output tokens.
