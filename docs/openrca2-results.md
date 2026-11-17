# OpenRCA 2.0: the held-out result

The final test of the design in `docs/openrca2-design.md`, run once on 2026-11-16. **The bar is met:** the design made 245 exact matches on the 355 held-out cases against 186 for the standard agent on the same model, 69.0% against 52.4%.

## What was run

- **The design:** `--agent lead+survey+kind2`. Code surveys the case's telemetry (every service, the calls between them, the entry services); a lead agent investigates with read-only SQL tools and drafts an answer; a subagent in a fresh context tests the kind of each fault in the draft, with a table of the claimed service's calls computed by code; the lead writes the final answer.
- **The comparison:** the leaderboard's standard agent, rebuilt (`docs/openrca2-baseline.md`): one model in a loop with the same tools.
- **Both on Claude Haiku 5.5**, on the same 355 held-out cases (TrainTicket 215, Hotel Reservation 115, OTel Demo 25), with the same tools and scorer.
- **Blind:** the held-out telemetry and answers were never opened during development. Both runs answered every case before any answer was read; `flowguard.openrca2.final` then scored each saved answer once. No case failed and none was rerun. The configuration, the bar and the scorer were fixed before the test.

## Result

| System | Cases | Standard agent, exact | Design, exact | Won | Lost | p |
|---|---|---|---|---|---|---|
| Hotel Reservation | 115 | 101 (87.8%) | 103 (89.6%) | 10 | 8 | 0.81 |
| OTel Demo | 25 | 12 (48.0%) | 20 (80.0%) | 9 | 1 | 0.02 |
| TrainTicket | 215 | 73 (34.0%) | 122 (56.7%) | 58 | 9 | 7 × 10⁻¹⁰ |
| **All** | **355** | **186 (52.4%)** | **245 (69.0%)** | **77** | **18** | **7 × 10⁻¹⁰** |

Won: the design is right where the standard agent is wrong. Lost: the reverse. p is the exact paired sign test on those cases.

- **The bar** (more exact matches, p < 0.05): met. The gain is 59 cases, 16.6 points, with a 95% interval of 11.5 to 21.7 points. The 95% intervals of the two rates are 47.2 to 57.5% and 64.0 to 73.6%.
- **The gain is in TrainTicket and OTel Demo.** On Hotel Reservation the two agents cannot be told apart.

| Score, all 355 cases | Standard agent | Design |
|---|---|---|
| Exact match (acc) | 0.524 | 0.690 |
| F1 | 0.559 | 0.723 |
| Any-hit / all-hit (the right service named) | 0.944 / 0.921 | 0.975 / 0.955 |
| Type-acc (the right kind, where the service is right) | 0.610 | 0.759 |
| Node-F1 / edge-F1 (the propagation) | 0.902 / 0.817 | 0.905 / 0.831 |
| Path-acc | 0.567 | 0.734 |
| Cost a case | 3.0 cents | 4.7 cents |
| Time a case | 1.3 min | 2.2 min |
| Tool calls a case | 28.6 | 20.4 |

**Under the public scorer's rule.** The table above scores by the roles in `label.json`: only the faults marked required must be named. The public scorer requires every injected fault, including those the labels mark optional or not effective. Both agents score lower under it, and the design still leads:

| System | Cases | Standard agent, exact | Design, exact |
|---|---|---|---|
| Hotel Reservation | 115 | 53 | 55 |
| OTel Demo | 25 | 7 | 12 |
| TrainTicket | 215 | 51 | 79 |
| **All** | **355** | **111 (31.3%)** | **146 (41.1%)** |

Case by case under this rule the design won 51 and lost 16 (p = 2 × 10⁻⁵). The bar was fixed on the first rule; this one is reported beside it, as agreed.

Per case: `reports/openrca2-heldout-standard/`, `reports/openrca2-heldout-design/`; the comparison as printed: `reports/openrca2-heldout-compared.md`.

## What the result shows

- **The gain is in naming the kind of fault.** Both agents nearly always find the faulty service (any-hit 0.94 and 0.98). The standard agent names the right kind for 61% of the services it gets right, the design for 76%. This is the failure the development analysis found and the design was built against.
- **The kind check carries most of it.** The lead's drafts, before any check, were right in 198 cases; the finals in 245. The check fixed 60 drafts and broke 13. The drafts alone (lead and survey) are 12 cases above the standard agent.
- **The development cases predicted the held-out cases.** The design scored 71% on the 100 development cases and 69.0% here; the standard agent 54% and 52.4%. By system the design had 94%, 86% and 57% on development and 90%, 80% and 57% here. The choices made on the development cases did not overfit them.
- **The cost is 1.6 times the standard agent's** in money and 1.8 times in time, for 1.3 times the exact matches.

## What it does not show

- **It is not a leaderboard result.** The published rows were measured on an older, 500-case version of the data, with other labels and models (best row on 2026-11-12: 46.40%). This test compares two agents on one model under this project's rebuild of the scorer. A claim against the leaderboard needs a submission under its rules.
- **One run of each agent.** On development cases two runs of the same agent differ in about 12 cases in 100, with equal totals. A net gain of 59 in 355 is far outside that, but each per-system count is one noisy reading; OTel Demo has 25 cases.
- **One model.** Whether the gain holds on a stronger model, where the standard agent names kinds better, is not tested.
- **It costs something on Hotel Reservation.** Exact matches are level there, but the design's propagation is worse (edge-F1 0.904 against 0.966) and its F1 slightly lower (0.929 against 0.942), at 1.6 times the cost.
- **TrainTicket is still 57%.** 93 of its 215 cases are missed. From the development cases: network faults to MySQL drafted as database faults, HTTP faults read as network faults (the third version of the check fixed this on development cases but was not kept), and loss and corruption, which the telemetry does not separate.
- **Injected faults.** Every case is one or more faults injected into a test system. Real incidents are not labelled this way, and nothing here measures them.

## The held-out cases are spent

They were run once and scored once. Nothing is tuned, selected or rerun on them. Any further work is developed on the development cases and would need new cases for a new test.
