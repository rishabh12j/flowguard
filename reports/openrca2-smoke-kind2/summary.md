# Baseline run: claude:claude-haiku-5-5, 1 development cases

| Score | Mean |
|---|---|
| f1 | 1.000 |
| precision | 1.000 |
| recall | 1.000 |
| acc | 1.000 |
| any_hit | 1.000 |
| all_hit | 1.000 |
| type_acc | 1.000 |
| node_f1 | 0.800 |
| edge_f1 | 0.667 |
| path_acc | 1.000 |
| path_acc_service | 1.000 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-337 | hs | 15 | 14 | 417,861 | 28,682 | 0.032 | 135 | 1 | 1.00 | 1 | the model stopped calling tools |  |

Total: $0.03, 417,861 prompt tokens, 28,682 output tokens.
