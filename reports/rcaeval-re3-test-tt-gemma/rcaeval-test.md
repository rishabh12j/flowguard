# RCAEval RE3: root-cause service, test

Model: `gemma4:12b, diagnosis explain`. Code from commit `c591cb7`.

| | Result |
|---|---|
| Named the right service | 12 of 30, 40% (25% to 58%) |
| Interval counting families | 15% to 71% |
| - with a diagnosed cause | 12 |
| - located, cause unexplained | 0 |
| Named a wrong service | 17 |
| Abstained | 1 (named the right service anyway in 0) |
| Right when it named a service | 41% |
| Baseline: the deepest service with a new error | 17% |
| Baseline: always ts-auth-service | 50% |
| Baseline: first error's service | 40% |

| By | Diagnosed right | Located right | Wrong | Abstained |
|---|---|---|---|---|
| f1 | 3 | 0 | 3 | 1 |
| f2 | 3 | 0 | 4 | 0 |
| f3 | 6 | 0 | 4 | 0 |
| f4 | 0 | 0 | 6 | 0 |
| ts-auth-service | 0 | 0 | 14 | 1 |
| ts-route-service | 12 | 0 | 3 | 0 |

Abstentions:

- 1: no service shows a new or increased error since the failure began
