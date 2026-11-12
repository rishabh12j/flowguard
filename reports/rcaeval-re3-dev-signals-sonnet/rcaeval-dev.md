# RCAEval RE3: root-cause service, dev

Model: `claude-sonnet-5-5, diagnosis explain`. Code from commit `565ef66`.

| | Result |
|---|---|
| Named the right service | 21 of 30, 70% (52% to 83%) |
| Interval counting families | 40% to 89% |
| - with a diagnosed cause | 6 |
| - located, cause unexplained | 15 |
| Named a wrong service | 0 |
| Abstained | 9 (named the right service anyway in 0) |
| Right when it named a service | 100% |
| Baseline: the deepest service with a new error | 83% |
| Baseline: always carts | 40% |
| Baseline: first error's service | 30% |

| By | Diagnosed right | Located right | Wrong | Abstained |
|---|---|---|---|---|
| f1 | 3 | 7 | 0 | 0 |
| f2 | 0 | 3 | 0 | 0 |
| f3 | 3 | 5 | 0 | 2 |
| f4 | 0 | 0 | 0 | 7 |
| carts | 0 | 7 | 0 | 5 |
| front-end | 4 | 4 | 0 | 1 |
| orders | 2 | 4 | 0 | 3 |

Abstentions:

- 9: the symptoms show an isolated problem, not a sustained failure
