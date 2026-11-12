# RCAEval RE3: root-cause service, dev

Model: `gemma4:12b, diagnosis explain`. Code from commit `565ef66`.

| | Result |
|---|---|
| Named the right service | 18 of 30, 60% (42% to 75%) |
| Interval counting families | 39% to 78% |
| - with a diagnosed cause | 18 |
| - located, cause unexplained | 0 |
| Named a wrong service | 6 |
| Abstained | 6 (named the right service anyway in 0) |
| Right when it named a service | 75% |
| Baseline: the deepest service with a new error | 83% |
| Baseline: always carts | 40% |
| Baseline: first error's service | 30% |

| By | Diagnosed right | Located right | Wrong | Abstained |
|---|---|---|---|---|
| f1 | 8 | 0 | 2 | 0 |
| f2 | 2 | 0 | 1 | 0 |
| f3 | 4 | 0 | 2 | 4 |
| f4 | 4 | 0 | 1 | 2 |
| carts | 4 | 0 | 5 | 3 |
| front-end | 7 | 0 | 1 | 1 |
| orders | 7 | 0 | 0 | 2 |

Abstentions:

- 4: the model could not diagnose the incident: the answer broke the schema
- 2: the symptoms show an isolated problem, not a sustained failure
