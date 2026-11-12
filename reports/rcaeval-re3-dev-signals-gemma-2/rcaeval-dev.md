# RCAEval RE3: root-cause service, dev

Model: `gemma4:12b, diagnosis explain`. Code from commit `565ef66`.

| | Result |
|---|---|
| Named the right service | 22 of 30, 73% (56% to 86%) |
| Interval counting families | 56% to 86% |
| - with a diagnosed cause | 22 |
| - located, cause unexplained | 0 |
| Named a wrong service | 6 |
| Abstained | 2 (named the right service anyway in 0) |
| Right when it named a service | 79% |
| Baseline: the deepest service with a new error | 83% |
| Baseline: always carts | 40% |
| Baseline: first error's service | 30% |

| By | Diagnosed right | Located right | Wrong | Abstained |
|---|---|---|---|---|
| f1 | 8 | 0 | 2 | 0 |
| f2 | 2 | 0 | 1 | 0 |
| f3 | 7 | 0 | 2 | 1 |
| f4 | 5 | 0 | 1 | 1 |
| carts | 6 | 0 | 5 | 1 |
| front-end | 7 | 0 | 1 | 1 |
| orders | 9 | 0 | 0 | 0 |

Abstentions:

- 2: the symptoms show an isolated problem, not a sustained failure
