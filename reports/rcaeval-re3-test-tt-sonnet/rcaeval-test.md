# RCAEval RE3: root-cause service, test

Model: `claude-sonnet-5-5, diagnosis explain`. Code from commit `c591cb7`.

| | Result |
|---|---|
| Named the right service | 12 of 30, 40% (25% to 58%) |
| Interval counting families | 15% to 71% |
| - with a diagnosed cause | 4 |
| - located, cause unexplained | 8 |
| Named a wrong service | 12 |
| Abstained | 6 (named the right service anyway in 0) |
| Right when it named a service | 50% |
| Baseline: the deepest service with a new error | 17% |
| Baseline: always ts-auth-service | 50% |
| Baseline: first error's service | 40% |

| By | Diagnosed right | Located right | Wrong | Abstained |
|---|---|---|---|---|
| f1 | 1 | 2 | 1 | 3 |
| f2 | 1 | 2 | 2 | 2 |
| f3 | 2 | 4 | 4 | 0 |
| f4 | 0 | 0 | 5 | 1 |
| ts-auth-service | 0 | 0 | 9 | 6 |
| ts-route-service | 4 | 8 | 3 | 0 |

Abstentions:

- 5: the symptoms show an isolated problem, not a sustained failure
- 1: no service shows a new or increased error since the failure began
