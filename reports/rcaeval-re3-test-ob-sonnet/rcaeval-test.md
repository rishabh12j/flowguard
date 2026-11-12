# RCAEval RE3: root-cause service, test

Model: `claude-sonnet-5-5, diagnosis explain`. Code from commit `c591cb7`.

| | Result |
|---|---|
| Named the right service | 21 of 30, 70% (52% to 83%) |
| Interval counting families | 40% to 89% |
| - with a diagnosed cause | 3 |
| - located, cause unexplained | 18 |
| Named a wrong service | 9 |
| Abstained | 0 (named the right service anyway in 0) |
| Right when it named a service | 70% |
| Baseline: the deepest service with a new error | 17% |
| Baseline: always emailservice | 50% |
| Baseline: first error's service | 30% |

| By | Diagnosed right | Located right | Wrong | Abstained |
|---|---|---|---|---|
| f1 | 3 | 3 | 3 | 0 |
| f2 | 0 | 3 | 0 | 0 |
| f3 | 0 | 3 | 3 | 0 |
| f4 | 0 | 3 | 3 | 0 |
| f5 | 0 | 6 | 0 | 0 |
| adservice | 0 | 9 | 0 | 0 |
| cartservice | 3 | 0 | 0 | 0 |
| currencyservice | 0 | 0 | 3 | 0 |
| emailservice | 0 | 9 | 6 | 0 |
