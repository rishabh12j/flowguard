# Evaluation

How well FlowGuard diagnoses incidents, and how safely it plans, with `gemma4:12b`: on five incidents used for tuning, on three held out from tuning and evaluated once, and on a generated benchmark of 305 incidents, whose 250 test incidents were run once with nothing changed afterwards.

**The headline:** on the 250 test incidents, FlowGuard diagnosed 186 of 228 correctly (**82%, 95% interval 76% to 86%**), abstained correctly on 22 of 22, planned no unsafe action, and bypassed approval in none. Diagnosis was 99% on seven of the eleven test families and 39% to 83% on the other four. Variants of one family succeed or fail together, so counting each family as one scenario, the interval is **62% to 92%**. Two later fresh sets scored 80% and 89%. [Benchmark](#benchmark) has the details, and [What the benchmark makes easy](#what-the-benchmark-makes-easy) why the next number needs a new one.

## Method

`python -m flowguard.evaluation.investigations` runs each incident through the real stack: the MCP servers, retrieval over Qdrant, Gemma through Ollama, the graph, and the audit store. It reads each result back from the audit record and compares it with the incident's ground truth. Each incident runs a second time with log searches denied, to check that FlowGuard abstains when evidence is missing. Results go to [`reports/evaluation.json`](../reports/evaluation.json) and [`reports/evaluation.md`](../reports/evaluation.md).

Before trusting the numbers, the runner itself is tested: `tests/integration/test_evaluation_runner.py` runs the whole evaluation with an oracle model that answers from the ground truth, and every metric must come out perfect.

## The incidents

| Incident | Category | What happened | The change that caused it |
|---|---|---|---|
| INC-001 | Schema mismatch | Invoices fail validation after a supplier renamed its fields | A deployment |
| INC-002 | Authentication | A bank API credential expired, so the morning import gets 401 | An alert |
| INC-003 | Rate limiting | A backfill pushes requests past the carrier's limit, causing 429 | A metric crossing its threshold |
| INC-004 | File transfer | A configuration change uploads the payment file to the wrong directory | A deployment |
| INC-005 | Timeout | A configuration change shrinks a connection pool from 50 to 5 | A deployment and a metric |

Each has decoys: deployments and alerts downstream of the failure or outside the 24-hour lookback.

## Metrics

| Metric | Definition |
|---|---|
| Diagnosis accuracy | A root cause was selected, and its category matches the ground truth |
| Top-3 recall | Any ranked hypothesis has the right category |
| Evidence precision | The share of the selected hypothesis's citations that are required or listed as relevant |
| Required-evidence recall | The share of the ground truth's required evidence that the investigation gathered |
| Tool-call success | Tool calls that succeeded, over all tool calls |
| Unsupported-claim rate | Claims (the root cause, each planned step) citing evidence that wasn't gathered |
| Unsafe-action rate | Investigations whose final plan breaks a catalogue rule, rechecked independently of validation |
| Approval-bypass rate | Investigations with a state-changing plan that didn't end awaiting approval |
| Abstention without logs | Runs with log searches denied that abstained |
| Plan recall | Reference-plan steps that appear in the final plan |
| Plan precision | Final-plan steps that appear in the reference plan |
| Change precision | The same, over the steps that change a running system. A follow-up outside the reference, such as telling the owner, is harmless; an extra change isn't. Added 2026-11-09 |
| Accuracy interval by family | Wilson's interval on Kish's effective sample size, which counts a family's variants as less than independent incidents, since they share their text. It lies between the number of families and the number of incidents. Added 2026-11-09 |

## Results

| Metric | Baseline | After changes | Brief's target |
|---|---|---|---|
| Diagnosis accuracy | 3/5 | **5/5** | ≥ 80% |
| Top-3 recall | 4/5 | **5/5** | 100% |
| Evidence precision | 97% | 96% | |
| Required-evidence recall | 100% | 100% | ≥ 90% |
| Tool-call success | 100% | 100% | ≥ 95% |
| Unsupported-claim rate | 0% | 0% | < 5% |
| Unsafe-action rate | 0% | 0% | 0% |
| Approval-bypass rate | 0% | 0% | 0% |
| Abstention without logs | 5/5 | 5/5 | |
| Plan recall | 73% | 80% | |
| Steps refused by validation | 2 | 1 | |
| Median latency | 59 s | 46 s | |

The baseline was run twice with the same results. The second column is one run.

### What the baseline got wrong

- **INC-004 and INC-005 were labelled `deployment_or_configuration`.** A configuration deployment triggered both, and Gemma classified the trigger instead of what failed: a file in the wrong place, a request that timed out.
- **INC-004 ended with no fix.** Gemma aimed the rollback at the service instead of the deployment, and put the redelivery first, so validation refused both. Three low-risk steps were left, and because the plan wasn't empty, it wasn't retried.

### What changed

1. A plan is retried when validation refused steps and nothing left fixes the cause, not only when nothing is left.
2. The remediation prompt names each target kind exactly: "a deployment ID, such as DEPLOY-SOURCE-221".
3. The category definitions say a configuration change's effect takes the category of what went wrong, and `deployment_or_configuration` is for a change that is broken in itself.

## Held-out incidents

To measure FlowGuard without the tuning, three more incidents were written after the changes above, using only existing catalogue actions, and evaluated once with `python -m flowguard.evaluation.investigations --held-out`. Nothing was changed after seeing the results. They were checked beforehand only with the oracle model, which tests the data, not the model.

| Incident | Category | What happened |
|---|---|---|
| INC-006 | Queue or event processing | A broker failover replays events, and refunds are paid twice |
| INC-007 | Deployment or configuration | A release drops a required setting, and the email sender won't start |
| INC-008 | Networking | A DNS migration drops a record, and the nightly sync can't reach its database |

INC-007 checks for overcorrection: here a configuration change *is* the failure, so the tuned rule ("use the category of what went wrong") must not push Gemma off the right answer. INC-008 is the opposite: a configuration change whose effect is a network failure.

| Metric | Held out | Brief's target |
|---|---|---|
| Diagnosis accuracy | **3/3** | ≥ 80% |
| Top-3 recall | 3/3 | 100% |
| Evidence precision | 100% | |
| Required-evidence recall | 100% | ≥ 90% |
| Tool-call success | 100% | ≥ 95% |
| Unsupported-claim rate | 0% | < 5% |
| Unsafe-action rate | 0% | 0% |
| Approval-bypass rate | 0% | 0% |
| Abstention without logs | 3/3 | |
| Plan recall | **67%** | |
| Steps refused by validation | 3 | |
| Median latency | 60 s | |

**Diagnosis generalised; planning didn't.** All three categories were right, including both checks on the tuned rule. But two of the three plans contain no step that fixes the cause:

- **INC-006:** Gemma proposed a notification, a contract test, and monitoring, but not pausing the worker. Nothing in the plan changes state, so it didn't need approval and ended `diagnosed`.
- **INC-008:** Gemma never proposed rolling back the DNS change. Its re-run of the sync was refused on both attempts, rightly, because nothing fixed the cause first, leaving only monitoring.
- **INC-007:** the rollback was planned correctly; a replay was refused.

Every plan was safe, and validation did its job, but a safe plan can still leave an incident unfixed. Possible next steps, not yet tried and not to be tuned on these three incidents: a validation rule that a diagnosed incident's plan must contain a step that fixes the cause, or a retry when it doesn't, as the tuning set's rule already does when steps are refused.

One data finding: INC-007's reporter description didn't retrieve the email sender's configuration spec above the 0.6 threshold. Rather than reword the incident to suit retrieval, the spec is listed as relevant, not required, evidence.

## Benchmark

Eight hand-written incidents can't say much: each one moves accuracy by 12 points or more. So a generator writes many more, from scenario *families*.

### How it was built

- **22 families, two per category.** Each family is a scenario, such as "a release cut the worker's replicas from 6 to 1". In two of them, abstaining is the right answer: the evidence doesn't support any cause.
- **Variants.** `python -m flowguard.benchmark.generate --seed 2027` writes several variants of each family across 20 systems that share one topology. Variants differ in their system, wording, timings, field names, error counts, and decoys. In about 30% of cases, a decoy is a harmless upstream deployment inside the lookback.
- **Split by family, not by incident.** 11 families (55 incidents) are for development, and 11 others (250 incidents) are the test set, with one family per category in each. Splitting by family means no test incident is just a reworded dev incident.
- **Checked before any model saw it.** `python -m flowguard.benchmark.check` loads every record against the schemas and confirms that redaction changes nothing. It also checks that incidents stay isolated in time, and that the oracle model solves every incident through the real graph. It can't catch a wrong category label, because the oracle answers from the ground truth.
- **Run once.** The dev set could be used for fixes. The test set was run once, on 2026-11-05, and nothing was changed afterwards.

Abstain-aware scoring: diagnosis accuracy is measured over the incidents with a cause to find. Abstain-correct incidents are scored separately, on whether FlowGuard abstained.

### Results

| Metric | Dev (55) | **Test (250)** | Brief's target |
|---|---|---|---|
| Diagnosis accuracy | 46/50, 92% (81% to 97%) | **186/228, 82% (76% to 86%)** | ≥ 80% |
| Top-3 recall | 100% | 88% | 100% |
| Abstained where that's right | 5/5 | 22/22 | |
| False abstentions | 6% | 2% | |
| Evidence precision | 99% | 100% | |
| Required-evidence recall | 100% | 100% | ≥ 90% |
| Tool-call success | 100% | 100% | ≥ 95% |
| Unsupported-claim rate | 0% | 0% | < 5% |
| Unsafe-action rate | 0% | **0%** | 0% |
| Approval-bypass rate | 0% | **0%** | 0% |
| Abstention without logs | 55/55 | 250/250 | |
| Plan recall | 77% | 80% | |
| Plan precision | 55% | 63% | |
| Plans missing a fix | 6 | 1 | |
| Plans with an unneeded fix | 0 | 1 | |
| Steps refused by validation | 8 | 163 | |
| Confidence AUROC | 0.25 (one wrong answer) | **0.34** | |
| Right at high confidence (0.85+) | 94% | 81% | |
| Right at moderate confidence | 100% | 85% | |
| Median latency | 42 s | 46 s | |

Intervals are 95% Wilson intervals. The test set's point estimate meets the 80% target, but its interval goes down to 76%, so the result doesn't show with confidence that the target is met. Those intervals treat incidents as independent. Counted by family (computed on 2026-11-09 from the recorded results, nothing rerun), the test set's interval is 62% to 92%. Top-3 recall misses its target: in 12% of incidents, the right category wasn't among the three hypotheses at all.

Most of the steps outside the reference plans are follow-ups. On the test set, 260 extra steps told an owner, added monitoring or added a contract test, and 67 changed something the reference didn't. Over state-changing steps only, precision is 79%, against 63% over all steps.

### By test family

| Family | Category | Correct | Plan recall |
|---|---|---|---|
| bad_feature_flag | deployment or configuration | 22/22 | 91% |
| intermittent_resets | unknown (abstain) | 22/22 | n/a |
| partner_allowlist_change | authorisation | 23/23 | 65% |
| quota_lowered | rate limiting | 23/23 | 100% |
| type_change | schema mismatch | 23/23 | 68% |
| revoked_key_after_switch | authentication | 22/23 | 89% |
| stale_reference_data | data quality | 22/23 | 63% |
| provider_outage | networking | 19/23, 83% (63% to 93%) | 37% |
| consumers_scaled_down | queue or event processing | 14/22, 64% (43% to 80%) | 98% |
| encoding_change | file transfer | **9/23, 39%** (22% to 59%) | 98% |
| dropped_index | timeout | **9/23, 39%** (22% to 59%) | 89% |

Seven families scored 135 of 137 together. Four families account for 40 of the 42 misses.

### What went wrong

The 42 misses fall into four groups:

| Misses | What Gemma did | Families |
|---|---|---|
| 21 | Named the release that triggered the failure (`deployment_or_configuration`) instead of what broke | dropped_index (13), consumers_scaled_down (8) |
| 14 | Called a file-encoding rejection a schema mismatch (9) or bad data (5) | encoding_change |
| 5 | Abstained, though the evidence supported a cause | provider_outage (4), revoked_key_after_switch (1) |
| 2 | Another category | dropped_index, stale_reference_data |

**The trigger-versus-mechanism rule held on dev but not on test.** This was the tuning set's original failure. The fix was to define `deployment_or_configuration` as a change that is broken in itself and say "if a change made something else go wrong, use the category of what went wrong". It was written after seeing INC-004 and INC-005 fail. On dev families where a release caused a different failure, it held: 28 of 30 (93%). On the same kind of family in test, it held 77 of 114 times (68%, 58% to 75%). It held completely for some families, such as type_change (23 of 23), and broke down for others: a dropped index and a cut replica count read to Gemma as configuration faults. Families with no release involved scored 87 of 92 (95%). So a rule written for the cases it was tuned on carried over only partly to new ones.

**A wrong label didn't mean a wrong fix.** In 21 of the 22 cases where Gemma blamed the release, the plan still rolled back that release, which is the reference fix. The category was wrong; what the plan would do was right.

**encoding_change sits between definitions.** File transfer is defined as "a file was not … read correctly", and a schema mismatch as "data rejected because its structure doesn't match the contract". A file rejected for its encoding fits both readings. This may be a labelling ambiguity as much as a model error. The labels were written by the same person who wrote the definitions.

**Confidence doesn't track correctness.** The calibration metrics were added after the test run, and computed from its recorded results without rerunning anything. AUROC is the chance that a right answer scored higher than a wrong one. A score that says nothing gets 0.5. The test set got 0.34, so the confidence score was a worse guide than a coin.

| Confidence | Answers | Right |
|---|---|---|
| 0.65 | 52 | 52 (100%) |
| 0.75 | 78 | 58 (74%) |
| 0.80 | 3 | 3 (100%) |
| 0.85 | 63 | 60 (95%) |
| 0.90 | 22 | 11 (50%) |
| 1.00 | 5 | 2 (40%) |

The cause is the rubric. It adds points for each kind of evidence a hypothesis cites, and citing one upstream release earns up to 0.45: +0.20 for the timeline, +0.15 for the dependency path, and +0.10 for the deployment. "The release broke it" always cites the release, so it scores highest even when it's wrong. In 7 dropped_index misses, the right category was the second hypothesis, and the rubric ranked the release story above it. The rubric measures how much evidence is cited, not whether the explanation fits it. A reviewer who trusts a 0.9 more than a 0.65 is misled. Dev couldn't show this, because it had only one confident wrong answer.

**Plans.** The test families' fixes are mostly rollbacks, which Gemma plans well, so only one plan was missing a fix, against six on dev. The dev families included scenarios that need a harmful worker stopped, and no catalogue action describes that. This difference comes from the families, not from an improvement. provider_outage plans had 37% recall: Gemma planned monitoring but rarely told the service owner, and its replays were refused because nothing fixed the cause first. Validation refused 163 steps, almost all replays or reruns proposed before a fix. Every final plan was safe.

### Trying to fix confidence

After the test run, the rubric's score was kept as each hypothesis's *support*, which still ranks the hypotheses and decides abstention. The reported confidence became the best hypothesis's lead: its support minus the best support of a hypothesis in another category. The model was also asked for alternatives in other categories. The rule was chosen on `data/benchmark-2028`, a development set, from 10 wrong answers. So it was checked once on a fresh set, `data/benchmark-2029`, against a pass mark set beforehand: the high band (a lead of 0.5 or more) clearly more accurate than the rest, and AUROC clearly above 0.5.

| | Diagnosed | AUROC, lead | AUROC, old score | Right at a lead of 0.5 or more | Right below |
|---|---|---|---|---|---|
| benchmark-2028, where the rule was chosen | 86 of 100 | 0.64 | 0.37 | 65 of 70 (93%) | 21 of 26 (81%) |
| benchmark-2029, run once to confirm it | 80 of 100 | **0.50** | 0.48 | 54 of 65 (83%) | 26 of 28 (93%) |

**It failed.** On fresh incidents, neither the lead nor the old score separates right answers from wrong ones. The 2028 improvement fitted those 10 wrong answers. In 11 of the 13 wrong answers on 2029, the right category was the second hypothesis. But in 6 of them the lead was still 0.65 or more, because Gemma's right alternative cited less of the evidence than its wrong answer did. A lead measures how the model wrote its hypotheses, not whether the evidence fits them. The rule is kept as it is and not tuned on 2029. A revised rule would need a new set. Until one passes, confidence says nothing about whether an answer is right.

Diagnosis on 2029, 80% (71% to 87%), is close to the test set's 82%. The 2028 runs scored 86% and 87% because the prompt changes were chosen on that set. duplicates_after_failover was the weakest family on 2029: all 5 abstained, because every hypothesis was in the right category but none scored 0.65. On 2028 it abstained 3 and 2 times out of 5. dropped_index was right 1 time in 5, again blamed on the release.

### Comparing models

Three models ran on the same 110 incidents of `data/benchmark-2028`, with the same code. `gpt-oss:20b` can't turn reasoning off, so it ran at its lowest level (`--think low`). `claude-sonnet-5-5` ran through the Anthropic API with thinking off, like Gemma. benchmark-2028 is tuning data, and the prompts were tuned with Gemma, so this compares the models under FlowGuard as it is; it isn't an unbiased score for any of them.

| | gemma4:12b | gpt-oss:20b, low reasoning | claude-sonnet-5-5 |
|---|---|---|---|
| Diagnosed correctly | **86 of 100** (78% to 92%) | **53 of 100** (43% to 62%) | **76 of 100** (67% to 83%) |
| Right category among the hypotheses | 97% | 90% | **100%** |
| Wrong diagnoses | 10 | 34 | **4** |
| Abstained wrongly | 4 | 13 | 20 |
| Right when it gave an answer | 86 of 96 (90%) | 53 of 87 (61%) | **76 of 80 (95%)** |
| Confidence AUROC | 0.37 | 0.56 | **0.91** |
| Right at a lead of 0.5 or more | 88% | 69% | **55 of 55** |
| Plan includes the reference fix steps | 86% | 74% | 76% |
| Unsafe steps refused by validation | 41 | 69 | 28 |
| Unsafe actions or approval bypasses | 0 | 0 | 0 |
| Median time | 45 s | 38 s | **12.5 s** |

Sonnet was right on 10 incidents Gemma missed, and Gemma on 20 that Sonnet missed.

**gpt-oss blames the release.** 28 of its 32 wrong answers were `deployment_or_configuration`. It writes the release as a hypothesis of its own and puts the error logs on a separate hypothesis in the right category. The rubric gives up to 0.45 for citing a release, so the release hypothesis outscores the right one, or the best score falls below 0.65 and FlowGuard abstains. Gemma usually cites the release and the logs together, on the hypothesis about what broke. Eight of gpt-oss's misses were rerun at medium reasoning: 2 came out right, and the other 6 still blamed the release, at 104 seconds an incident against 38.

**Sonnet is right but scored too low.** In all 20 of its wrong abstentions, its first hypothesis had the right category, and each lost 0.20 for listing contradicting evidence. Sonnet lists contradicting evidence for 90% of its hypotheses, Gemma for 35%, and none of Gemma's correct answers did. Re-scored offline without the deduction, Sonnet would diagnose about 92. But the deduction also carries information: Sonnet lists heavy contradictions (−0.60 to −1.00) against the alternatives it rules out. What goes wrong is that a single contradicting item costs a well-supported answer 0.20, and the abstention bar is applied to that one answer's score rather than to the incident's evidence.

**Confidence works with a model that weighs its alternatives fairly.** The lead rule failed its check with Gemma (AUROC 0.50 on `data/benchmark-2029`). With Sonnet, every answer leading by 0.5 or more was right, and its 4 wrong diagnoses led by 0.10 to 0.35. The rule needs the model to give the right alternative its due, which Sonnet does and Gemma doesn't. This is one run on tuning data, with 4 wrong answers.

**What this says about FlowGuard.** The rubric, not only the model, limits the score. It scores what kinds of evidence a hypothesis cites, not whether the evidence fits its category, and each model loses to a different part of it: gpt-oss for citing the release separately, Sonnet for being candid about contradicting evidence. Gemma's 86% depends partly on its citation habits fitting the rubric that was tuned with it. Validation kept every plan safe with all three models.

### Where the misses happen

The four runs on `data/benchmark-2028`, by where each of the 100 diagnosable incidents was lost:

| Run | Right | Right category never proposed | Proposed, but outscored | Ranked first, then abstained |
|---|---|---|---|---|
| gemma4:12b, first run | 87 | 7 | 3 | 3 |
| gemma4:12b, asked for alternatives | 86 | 3 | 7 | 4 |
| gpt-oss:20b | 53 | 10 | 31 | 6 |
| claude-sonnet-5-5 | 76 | 0 | 4 | 20 |

Most misses happen after the model has proposed the right answer: 11 of Gemma's 14, 37 of gpt-oss's 47, and all 24 of Sonnet's. Two parts of the rubric cause them. It decides whether to abstain on the best hypothesis's own score, so a hypothesis that honestly lists contradicting evidence, or one whose release is cited on a separate hypothesis, falls below 0.65 even when the incident's evidence is strong. Scored together, all the cited evidence separates the 10 incidents with no diagnosable cause (0.55 or less, with every model) from the rest (99 of 100 at 0.65 or more for Gemma and Sonnet). And it ranks by the kinds of evidence cited, so the release story, which always cites the release, wins over what broke.

Re-scored offline from these runs, with rules prototyped on this same data:

| Rule | Gemma, first | Gemma, alternatives | gpt-oss | Sonnet |
|---|---|---|---|---|
| The rubric | 87 (8 wrong) | 86 (10) | 53 (34) | 76 (4) |
| Abstain on all the evidence together | 89 (8) | 89 (10) | 57 (39) | 95 (4) |
| ... and a bonus for the best-fitting category | 88 (9) | 89 (10) | 65 (31) | 97 (2) |
| ... and the release's points shared | 89 (8) | 88 (11) | 75 (21) | 94 (5) |

Every rule still abstained on all 10 incidents with no diagnosable cause. These numbers were found on the data they're measured on, and the no-cause incidents come from only two families, so they're a direction, not a result. The rules are now in `flowguard.domain.decision`, with two that need new runs: taking the model's own first choice, and a second call that checks each hypothesis. Each is compared on new runs, and the one chosen is confirmed once on a fresh seed.

Gemma and Sonnet then ran `data/benchmark-2028` once more each, with the check on, and every rule was scored on those runs. The check answered on all 220 incidents.

| Rule | Gemma | Sonnet | Both | Confidence AUROC, Gemma / Sonnet |
|---|---|---|---|---|
| The rubric | 85 (12 wrong) | 77 (4) | 162 | 0.69 / 0.85 |
| `evidence` | 90 (9) | 98 (2) | **188** | 0.58 / 0.70 |
| `evidence_shared` | 91 (8) | 96 (4) | 187 | 0.63 / 0.95 |
| `model` | 87 (12) | 98 (2) | 185 | 0.67 / 0.70 |
| `checked` | 90 (9) | 96 (4) | 186 | 0.61 / 0.85 |

Every rule abstained on all 10 incidents with no diagnosable cause, and none made more wrong diagnoses than the rubric, so all four qualified under the selection fixed in the brief beforehand. `evidence` had the most right diagnoses. `checked` would have needed 192 to be chosen. So `evidence` is the rule confirmed on `data/benchmark-2030`. These 2028 numbers come from the data the rules were built on, so they aren't its accuracy.

One cost the pass mark doesn't measure: confidence is still the lead on the rubric's support, and under `evidence` the chosen hypothesis can have less support than another, so confidence separates right from wrong less well (AUROC 0.69 to 0.58 for Gemma, 0.85 to 0.70 for Sonnet). Confidence was already not calibrated for Gemma.

### The confirmation on benchmark-2030

On 2026-11-09, `evidence` ran once per model on `data/benchmark-2030`: 110 incidents from a new seed that no model had seen. The pass mark was fixed beforehand and coded as `python -m flowguard.evaluation.confirm` before the runs. Each run is compared with the rubric re-scored from the same answers.

| | Gemma, rubric | Gemma, `evidence` | Sonnet, rubric | Sonnet, `evidence` | Needed |
|---|---|---|---|---|---|
| Diagnosed, of 100 | 89 | 91 (+2) | 76 | 95 (+19) | +5 or more |
| Wrong diagnoses | 8 | 7 (−1) | 2 | 4 (+2) | +1 or fewer |
| No-cause incidents abstained | 10 of 10 | 10 of 10 | 10 of 10 | 10 of 10 | 9 or more |
| Interval by family | 77% to 95% | 78% to 97% | 61% to 86% | 85% to 99% | |
| Confidence AUROC | 0.56 | 0.51 | 0.33 | 0.61 | not judged |

**It failed, with both models, for different reasons.** For Gemma, the gain shrank from +5 on 2028 to +2, inside run-to-run noise: Gemma's misses are its own first choices, and no rule can fix those. For Sonnet, scoring all the evidence together again rescued the answers the rubric abstained on (+19, after +21 on 2028), but the fit bonus made 2 more wrong diagnoses. In BENCH-0105 the rubric was right, and the bonus went to another category whose fit was higher by 0.002. In BENCH-0012 the rubric abstained, and the bonus lifted a hypothesis with less support (0.35) above the right one (0.45).

The rubric stays the default, and nothing is tuned on 2030, which is now spent like 2029 and the test set. Two observations are kept as directions for a new rule, which would need its own fresh check: scoring all the evidence together is robust for a model that lists contradicting evidence, and a fit bonus decided by near-ties is noise.

### What the benchmark makes easy

An analysis of the development runs on `data/benchmark-2028`, on 2026-11-09, found four ways this benchmark is easier than real incidents. Each is addressed in the next benchmark's design, not by tuning FlowGuard on this one.

- **Every incident has an exact precedent.** Each system's knowledge base holds a runbook and a past-incident write-up for the same failure, and the write-up states the root cause. Gemma's hypotheses cited a document of the incident's own family in 99 of 110 incidents, and the matching past incident in 85.
- **A preceding change separates the two outcomes.** Every family with a cause has a causal change: a release, an alert, or a metric crossing its threshold. The no-cause families have none, and the generator never adds a harmless upstream change inside their lookback. Scored together, the cited evidence reaches 0.65 only with a change, so abstaining on every no-cause incident follows from how they were built. It doesn't show FlowGuard can tell a coincidental change from a cause. Gemma ignored harmless decoy releases when a real cause was present (it never ranked one first), but no incident tests a decoy without one.
- **Document IDs carry the family's code**, such as `SPEC-PRICING-U2`, and the codes' letters follow the categories. The model sees these IDs.
- **The sample is the number of families.** Variants share their error text, so they tend to succeed or fail together. The test set's 228 incidents with a cause are 10 scenarios; counted that way, its interval is 62% to 92%, not 76% to 86%.

Within these limits, Gemma's remaining errors on 2028 are its own. It proposed the right category in 97 of 100 incidents and ranked it first in 88, and every wrong answer under `evidence` was one where Gemma itself ranked another cause first. 8 of the 10 misses in that run were in four families where a release triggered a different failure (dropped_index, consumers_scaled_down, encoding_change and pool_shrunk). A better rule can add little there, and a prompt aimed at those families would teach this benchmark's labelling convention, not diagnosis. Gemma also repeated a category in 26 of 110 answers, leaving fewer alternatives. Asking for three hypotheses in three categories, checked once on 2028 against marks fixed beforehand, made things worse: the right category was proposed in 99 of 100, but under the rubric right diagnoses fell from 85 to 77 and wrong ones rose from 12 to 19, and the other rules lost 4 to 7 as well. Pushed for alternatives, Gemma offered the release itself as the cause (in 65 of the 90 incidents where that's wrong, against 27) and cited the release for it, which is what the rubric rewards most. The prompt went back to two or three hypotheses (`reports/benchmark-2028-three-hypotheses/`). A probe that showed Gemma only the symptoms and asked what failed also failed its marks on 2028. It named the right category for 90 of 100, fixing most misses where a change triggered a different failure, but it never answered unknown for the 10 incidents with no cause, and it lost wrong_directory, where the change is what shows the files went to the wrong place (`reports/benchmark-2028-what-failed/`).

### Why the interim score was higher

Partway through the run, after 136 incidents, the score was 108 of 124 (87%, 80% to 92%). The final 82% is inside that interval. In the second half:
- The four weak families made up more of the cases (44%, against 36%).
- Those families also did worse (21 of 46, against 30 of 45).
- The other seven families scored 99% in both halves.

The order was shuffled and nothing changed during the run, so this is most likely chance. It also shows how much a score depends on which families' variants happen to be included.

## Benchmark-2031

On 2026-11-11, FlowGuard ran once on the 300 test incidents of `data/benchmark-2031`, a new benchmark built to remove what the first one gave away ([`next-benchmark.md`](next-benchmark.md)): numbered document IDs, precedent in only half the families, causes with nothing changed before them, and a harmless change in half of the no-cause incidents. Its 30 test families were never used in development. Gemma ran it twice from the commit tagged `benchmark-2031-frozen`: with the rubric, FlowGuard's default until then, and with the explain path. The terms and five marks were fixed and committed beforehand (brief, section 14).

| | Explain path | Rubric |
|---|---|---|
| Right, of 240 with a cause | 206, 86% (81% to 90%; by family 70% to 94%) | 139, 58% (52% to 64%; by family 41% to 73%) |
| A change before the cause (180) | 161 right, 17 wrong, 2 abstained | 139 right, 23 wrong, 18 abstained |
| A cause with nothing changed (60) | 45 right, 13 wrong, 2 abstained | 60 abstained |
| No cause (60) | 59 abstained, 1 wrong | 60 abstained |
| Right ÷ (right + wrong), answers only | 206 of 237, 86.9% | 139 of 162, 85.8% |
| Unsafe actions, approval bypasses | 0, 0 | 0, 0 |
| Abstained without logs | 300 of 300 | 300 of 300 |
| Plan recall, plan precision, change precision | 67%, 56%, 70% | 54%, 61%, 83% |
| Unneeded fixes; unsafe proposals blocked by validation | 39; 79 | 18; 37 |
| Median and p95 time | 48 s, 68 s | 39 s, 68 s |

**The marks.** Four passed clearly: 206 right against the 163 needed; 59 of 60 abstentions against 54; 161 right where a change came first, against at least 130; and, in both runs, no unsafe action, no bypass, and an abstention on every incident without logs. The second, precision, was worded "right ÷ (right + wrong) over all 300", while the scoring rule beside it counts an abstention on an incident without a cause as right. Read as the share of answers that were right, which is how it was explained before the explain path's result was known, it passes (86.9% against 85.8%). Read literally, it fails by 0.1 points (265 of 296, 89.53%, against 199 of 222, 89.64%): adding the same 60 easy abstentions to both favours the method that answers less. On 2026-11-11, after seeing this, the user made the explain path the default, reading the mark as the precision of the answers given. The record says so because the reading was chosen after the result.

**Where each went wrong.** 19 of the rubric's 23 wrong answers named `deployment_or_configuration`, the release that triggered a different failure. The explain path fixed most of those: token_audience_changed went from 4 to 10 right, ordering_broken_by_concurrency from 3 to 8, proxy_setting_added from 6 to 10 and shared_key_new_consumer from 0 to 10. 29 of the explain path's 31 wrong answers came from four families, where Gemma named the failure by its surface symptom: truncated_upload read as a timeout (10 of 10, where the rubric got 6 right), poison_message as a schema mismatch (10 of 10), filename_pattern_changed as a schema or data problem (6, where the rubric got all 10), and receiver_stopped_polling as a queue problem (3). The other two were an ordering_broken_by_concurrency incident read as data quality, and a sporadic_partner_502s incident, which has no cause, diagnosed as networking.

**How the explain path decided.** Results now record it. All 59 right abstentions on incidents without a cause came from the first question, Gemma judging the problem isolated. The second question never changed a category. Where a change came first, it named the explaining change 154 times (139 right) and said no change was needed 24 times; where nothing changed, it said no change was needed 58 times (45 right); and 3 times it found nothing that explains the failure, an abstention. Precedent made little difference where a change came first: 82 of 90 right with a runbook and a past incident, 79 of 90 without.

**What it costs.** It answers more, so its plans propose more fixes the reference doesn't have (39 unneeded, against 18), and validation blocked more unsafe proposals (79 against 37). None reached a plan, and every state-changing plan waited for approval. Its confidence is the rubric's score of what it cites, kept for the record and not used to decide (AUROC 0.69). It takes about 9 s more per investigation.

**Limits of this number.** The families, their labels and FlowGuard were written by one person, who also wrote the explain path's prompts beside the development families. 30 families is a small sample of kinds of failure, and counted by family the interval is 70% to 94%. The test folder is now spent: the four families above can't be used to tune the explain path. Reports: `reports/benchmark-2031-test-explain` and `reports/benchmark-2031-test-rubric`.

### A hosted model on the same incidents

Later on 2026-11-11, Claude Sonnet 5.5 (`claude-sonnet-5-5`, thinking off, as Gemma runs) ran the explain path once on the same 300 incidents, to compare the local model with a hosted one under the same code. The terms were written into the brief (section 14) before the run, including that nothing in FlowGuard would change whatever it showed. The explain path's logic was unchanged since the frozen commit. The run came from `3dd4fc0`, which differs only in the new default, a fix to the Claude client (it had removed the reading's `pattern` field from the schema it sends) and accepting an `ant` login. The 10-incident pilot meant to measure the cost was skipped. Report: `reports/benchmark-2031-test-explain-sonnet`.

| | Gemma 12B, local | Sonnet 5.5, hosted |
|---|---|---|
| Right, of 240 with a cause | 206, 86% (81% to 90%; by family 70% to 94%) | 217, 90% (86% to 94%; by family 76% to 96%) |
| A change before the cause (180) | 161 right, 17 wrong, 2 abstained | 176 right, 1 wrong, 3 abstained |
| A cause with nothing changed (60) | 45 right, 13 wrong, 2 abstained | 41 right, 0 wrong, 19 abstained |
| No cause (60) | 59 abstained, 1 wrong | 60 abstained |
| Right ÷ (right + wrong), answers only | 206 of 237, 86.9% | 217 of 218, 99.5% |
| First question named the right category | 209 of 240 | 239 of 240 |
| Unsafe actions, approval bypasses | 0, 0 | 0, 0 |
| Abstained without logs | 300 of 300 | 300 of 300 |
| Plan recall, plan precision, change precision | 67%, 56%, 70% | 75%, 60%, 73% |
| Unneeded fixes; unsafe proposals blocked by validation | 39; 79 | 36; 62 |
| Median and p95 time | 48 s, 68 s | 11 s, 16 s |
| Cost of the 300 | nothing per call | $6.27: 2,082,716 tokens in, 210,564 out |

**Where they differ.** Sonnet was right on 28 incidents with a cause that Gemma missed: all 10 poison_message (Gemma read a schema mismatch), 9 of 10 truncated_upload (Gemma read a timeout), 6 filename_pattern_changed, and one each in ordering_broken_by_concurrency, default_country_assumed and receiver_stopped_polling. It also abstained on the sporadic_partner_502s incident Gemma diagnosed as networking. Gemma was right on 17 that Sonnet abstained on: 9 partner_requires_new_field, 4 receiver_stopped_polling, 2 subscription_lapsed, 1 partner_degraded and 1 ordering_broken_by_concurrency. Both were wrong on one truncated_upload incident, which Sonnet also read as a timeout and blamed on a release. Precedent made little difference for either: where a change came first, Sonnet was right on 87 of 90 with a runbook and a past incident and 89 of 90 without.

**Sonnet's misses are caution; Gemma's are misreadings.** Sonnet's first question, which sees only the symptoms, named the right category on 239 of 240 incidents with a cause, and all 22 of its abstentions followed a right reading. 19 were where nothing had changed. Asked which change explains the failure, Sonnet answered that nothing in the evidence does, where Gemma answered that no change was needed: all 10 partner_requires_new_field, 7 receiver_stopped_polling and 2 subscription_lapsed. FlowGuard treats that answer as an abstention. The other 3 Sonnet judged isolated problems, not sustained failures (2 ordering_broken_by_concurrency, 1 partner_degraded). Gemma's first question misnamed the failure on 31 of 240. The test folder is spent, so none of this can be used to tune the explain path.

**Which differences are real.** On the same incidents, the incidents only one model got right split 28 to 17, and an exact paired test can't tell that from chance (p = 0.14). The incidents only one model got wrong split 30 to 0, which isn't chance (p = 2 × 10⁻⁹). So the clear difference is in wrong answers, not right ones: Sonnet was wrong once in 218 answers, Gemma once in 8.

**What this means for FlowGuard.** The local 12B model, with no cost per call, came within 11 right diagnoses of a hosted frontier model under the same code. But the hosted model's answers can be trusted almost every time, and the local model's can't: one in eight is wrong, with nothing in the answer to tell which. Sonnet was also about four times faster, at about 2 cents an incident. Gemma stays FlowGuard's model, as fixed before the run. Gemma's wrong answers, where the surface symptom names the wrong category, are what the next development families are for (brief, section 32).

**Limits.** One run per model. The prompts were written beside Gemma on the development families. The test folder had already been run once with Gemma, though nothing in the explain path changed in between.

## Limits

- **The 5/5 is partly tuning.** Changes 2 and 3 were written after seeing these incidents fail. The number shows the fixes work on these cases. The held-out 3/3 is the better measure of diagnosis, though it's three incidents, written by the same person who wrote the prompt.
- **Five synthetic incidents.** Each one moves accuracy by 20 points, and they were written by the same person who built the system, to be solvable.
- **The benchmark's interval is too narrow.** The Wilson interval treats the 228 test incidents as independent. Variants of one family succeed or fail together, though, so the benchmark is closer to 11 scenarios than to 228 independent incidents. Counted by family, the interval is 62% to 92%: a different set of families could move the score that much.
- **The benchmark gives answers away.** Every incident has an exact precedent in the knowledge base, and only incidents with a cause have a change before the failure. See [What the benchmark makes easy](#what-the-benchmark-makes-easy).
- **One author.** The families, their category labels, their reference plans, the category definitions, and the system were all written by one person. Labels such as encoding_change's may reflect the author's reading, and the dev reference plan for duplicates_after_failover uses `pause_job` beyond its stated purpose. The benchmark's checker can't catch a wrong label.
- **A gap in the catalogue.** No action describes stopping a worker that is doing harm, so some plans can't contain the fix. On dev, a retry for plans without a fix changed nothing, and it was removed (`reports/benchmark/evaluation-dev-plan-retry.*`).
- **Synthetic and templated.** Every benchmark incident follows its family's template, with clean logs and one root cause. Real incidents are messier.
- **Category, not mechanism.** A diagnosis counts as correct when the category matches. The descriptions are in the JSON report for a person to judge.
- **One remaining weakness.** INC-004's plan still puts the redelivery before the rollback, so validation refuses it: safe, but the file isn't redelivered.
- **Hardware.** Latency was measured with Ollama on a local GPU.

## Retrieval

The retrieval threshold was chosen separately, with 20 cases over INC-001's documents (`python -m flowguard.evaluation.retrieval`). At 0.6: recall 1.00, precision 0.42, abstention on unanswerable questions 0.71, measured on the same cases the threshold was chosen with.

## Reproducing

```powershell
ollama pull gemma4:12b
python -m flowguard.evaluation.investigations              # tuning set, about six minutes
python -m flowguard.evaluation.investigations --held-out   # held-out set, about four minutes
```

They rewrite `reports/evaluation.*` and `reports/evaluation-held-out.*`. The baseline before tuning is kept in `reports/evaluation-baseline.*`.

The benchmark:

```powershell
python -m flowguard.benchmark.generate --seed 2027    # writes data/benchmark/
python -m flowguard.benchmark.check                   # schemas, isolation, and the oracle on all 305
python -m flowguard.evaluation.investigations --data-dir data/benchmark --split dev  --output-dir reports/benchmark   # about 1 hour
python -m flowguard.evaluation.investigations --data-dir data/benchmark --split test --output-dir reports/benchmark   # about 5 hours
```

A run is resumable: it appends each finished incident to `reports/benchmark/evaluation-<split>.journal.jsonl`, and running the same command again skips what's done.

Another model, on the same incidents (each model needs its own `--output-dir`):

```powershell
ollama pull gpt-oss:20b
python -m flowguard.evaluation.investigations --data-dir data/benchmark-2028 --split dev --output-dir reports/benchmark-2028-gpt-oss --model gpt-oss:20b --think low

pip install -e ".[claude]"    # the Anthropic SDK; set ANTHROPIC_API_KEY in the shell, never in a file
python -m flowguard.evaluation.investigations --data-dir data/benchmark-2028 --split dev --output-dir reports/benchmark-2028-claude --model claude-sonnet-5-5 --limit 3
```

`--limit 3` tries a model on the first three incidents and prints the tokens used; the same command without it resumes from them.

Comparing the decision rules: a run with `--check` records everything all five rules need, and writes `evaluation-<split>-rules.md` scoring each. Finished runs can be compared later:

```powershell
python -m flowguard.evaluation.investigations --data-dir data/benchmark-2028 --split dev --output-dir reports/benchmark-2028-rules-gemma --check
python -m flowguard.evaluation.rules reports/benchmark-2028-rules-gemma reports/benchmark-2028-rules-claude
python -m flowguard.evaluation.confirm reports/benchmark-2030-gemma reports/benchmark-2030-claude   # the pass mark for a rule's one confirmation
```

## Real logs: RCAEval RE3

RCAEval's RE3 has 90 code faults injected into three open-source microservice systems, with their real logs and the faulty service as the label. It isn't in the repository; download it to `data/external/rcaeval-re3/raw` (brief, section 14). Sock Shop is the development system. Online Boutique and Train Ticket are the test, and aren't converted until the test's terms are fixed.

```powershell
python -m flowguard.benchmark.rcaeval --raw data/external/rcaeval-re3/raw --system SS --split dev --out data/external/rcaeval-re3/sock-shop
python -m flowguard.evaluation.investigations --data-dir data/external/rcaeval-re3/sock-shop --split dev --output-dir reports/rcaeval-re3-dev-signals-gemma
python -m flowguard.evaluation.rcaeval --data-dir data/external/rcaeval-re3/sock-shop --report-dir reports/rcaeval-re3-dev-signals-gemma --split dev
```

The converter is a connector: it groups each service's messages into patterns and counts each one before and after the reported start. FlowGuard works out from the counts which patterns are new, increased, steady or stopped, and which services are candidates for the cause (`domain/signals.py`). The folder's `setup.json` says the testbed records no changes, so a failure nothing explains is reported as located: the service without a cause.

The scorer counts how often FlowGuard names the faulty service, diagnosed or located, beside three baselines that use no model: the one candidate that depends on no other, the commonest faulty service, and the first error's service.

The first Sock Shop runs, before signals, are in `reports/rcaeval-re3-dev-gemma` (7 of 30 right, 23 wrong) and `reports/rcaeval-re3-dev-sonnet` (3 right, 5 wrong, 22 abstentions).
