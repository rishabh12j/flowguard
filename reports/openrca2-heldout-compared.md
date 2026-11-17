# The final test: 355 held-out cases

| System | Cases | Standard agent, exact | Design, exact | Standard F1 | Design F1 |
|---|---|---|---|---|---|
| hs | 115 | 101 | 103 | 0.942 | 0.929 |
| otel-demo | 25 | 12 | 20 | 0.507 | 0.800 |
| ts | 215 | 73 | 122 | 0.360 | 0.604 |
| all | 355 | 186 | 245 | 0.559 | 0.723 |

Case by case, the design is right where the standard agent is wrong in 77 cases, and wrong where it is right in 18: p = 0.0000 (paired sign test).

**The bar** (more exact matches than the standard agent, p < 0.05): **met**.

## Under the public scorer's rule: every injected fault is required

| System | Cases | Standard agent, exact | Design, exact |
|---|---|---|---|
| hs | 115 | 53 | 55 |
| otel-demo | 25 | 7 | 12 |
| ts | 215 | 51 | 79 |
| all | 355 | 111 | 146 |

Case by case under this rule: 51 won, 16 lost, p = 0.0000. The bar is judged on the first table.

Cost: standard agent $10.77, design $16.84.
