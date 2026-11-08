# Evaluation

How well FlowGuard diagnoses incidents, and how safely it plans, with `gemma4:12b`: on five incidents used for tuning, on three held out from tuning and evaluated once, and on a generated benchmark of 305 incidents, whose 250 test incidents were run once with nothing changed afterwards.

**The headline:** on the 250 test incidents, FlowGuard diagnosed 186 of 228 correctly (**82%, 95% interval 76% to 86%**), abstained correctly on 22 of 22, planned no unsafe action, and bypassed approval in none. Diagnosis was 99% on seven of the eleven test families and 39% to 83% on the other four. [Benchmark](#benchmark) has the details.

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

Intervals are 95% Wilson intervals. The test set's point estimate meets the 80% target, but its interval goes down to 76%, so the result doesn't show with confidence that the target is met. Top-3 recall misses its target: in 12% of incidents, the right category wasn't among the three hypotheses at all.

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

### Why the interim score was higher

Partway through the run, after 136 incidents, the score was 108 of 124 (87%, 80% to 92%). The final 82% is inside that interval. In the second half:
- The four weak families made up more of the cases (44%, against 36%).
- Those families also did worse (21 of 46, against 30 of 45).
- The other seven families scored 99% in both halves.

The order was shuffled and nothing changed during the run, so this is most likely chance. It also shows how much a score depends on which families' variants happen to be included.

## Limits

- **The 5/5 is partly tuning.** Changes 2 and 3 were written after seeing these incidents fail. The number shows the fixes work on these cases. The held-out 3/3 is the better measure of diagnosis, though it's three incidents, written by the same person who wrote the prompt.
- **Five synthetic incidents.** Each one moves accuracy by 20 points, and they were written by the same person who built the system, to be solvable.
- **The benchmark's interval is too narrow.** The Wilson interval treats the 228 test incidents as independent. Variants of one family succeed or fail together, though, so the benchmark is closer to 11 scenarios than to 228 independent incidents. The interval describes more variants of these 11 families. A different set of families could move the score much more than 76% to 86% suggests.
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
```
