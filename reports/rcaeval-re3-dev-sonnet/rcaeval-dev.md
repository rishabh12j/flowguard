# RCAEval RE3: root-cause service, dev

Model: `claude-sonnet-5-5, diagnosis explain`. Code from commit `565ef66`.

| | Result |
|---|---|
| Right service | 3 of 30, 10% (4% to 26%) |
| Interval counting families | 3% to 31% |
| Wrong service | 5 |
| Abstained | 22 (named the right service anyway in 12) |
| Right when it answered | 38% |
| Baseline: always carts | 40% |
| Baseline: first error's service | 30% |

| By | Right | Wrong | Abstained |
|---|---|---|---|
| f1 | 1 | 0 | 9 |
| f2 | 0 | 0 | 3 |
| f3 | 2 | 3 | 5 |
| f4 | 0 | 2 | 5 |
| carts | 2 | 2 | 8 |
| front-end | 1 | 3 | 5 |
| orders | 0 | 0 | 9 |

Abstentions:

- 14: nothing in the evidence explains the failure
- 6: the symptoms don't show which category failed
- 2: the symptoms show an isolated problem, not a sustained failure
