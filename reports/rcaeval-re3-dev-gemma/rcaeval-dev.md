# RCAEval RE3: root-cause service, dev

Model: `gemma4:12b, diagnosis explain`. Code from commit `565ef66`.

| | Result |
|---|---|
| Right service | 7 of 30, 23% (12% to 41%) |
| Interval counting families | 8% to 53% |
| Wrong service | 23 |
| Abstained | 0 (named the right service anyway in 0) |
| Right when it answered | 23% |
| Baseline: always carts | 40% |
| Baseline: first error's service | 30% |

| By | Right | Wrong | Abstained |
|---|---|---|---|
| f1 | 3 | 7 | 0 |
| f2 | 0 | 3 | 0 |
| f3 | 2 | 8 | 0 |
| f4 | 2 | 5 | 0 |
| carts | 0 | 12 | 0 |
| front-end | 0 | 9 | 0 |
| orders | 7 | 2 | 0 |
