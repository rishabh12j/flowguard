# The next benchmark

A plan, written on 2026-11-09, for the benchmark that gives FlowGuard's next honest number. Every earlier set is now spent or tuning data, and [What the benchmark makes easy](evaluation.md#what-the-benchmark-makes-easy) explains why a new seed of the old families isn't enough. The benchmark was generated on 2026-11-10 (see [Generated](#generated)). The test folder ran once on 2026-11-11, under terms fixed beforehand, and is now spent (see [Result](#result)).

## What it fixes

| The old benchmark | The next one |
|---|---|
| Every incident has a runbook and a past-incident write-up for its own failure | Half the families have neither |
| Only incidents with a cause have a change before the failure | 8 families have a cause and no preceding change, and no-cause incidents get a coincidental change in half their variants |
| Document IDs carry the family code, such as `SPEC-PRICING-U2` | Document IDs are numbered |
| 22 families, so a test set of 11 families gives an interval of about ±15 points | 40 families: 30 in the test set, for about ±6 to ±8 |
| 2 no-cause families | 8 no-cause families |
| Clean logs | A few unrelated lines from other services, with every prompt kept inside Gemma's 8,192-token context |

## Design rules

1. **Labels follow the category definitions as written.** If a family's label sits between two definitions, as encoding_change's did between file transfer and schema mismatch, the family isn't used.
2. **What failed decides the category,** as the definitions say: a release that makes calls time out is `timeout`, not `deployment_or_configuration`.
3. **Precedent.** Within each group below, half the families, picked at random, have a runbook and a past-incident write-up for their kind of failure. The rest have neither. Every system keeps its API spec, and documents for other families remain as distractors.
4. **Changes.** The 24 families marked "Release" or "Partner alert" have a change before the failure. The 8 marked "Nothing changed" have none: no release, no alert, and no metric crossing a threshold. Each no-cause family gets a harmless upstream change inside the 24-hour lookback in half its variants. Families with a cause keep the old 30% chance of a harmless upstream decoy.
5. **Written before any model sees them.** Labels and reference plans are fixed first. The checker validates every incident with the oracle, as before. No model runs on a test family until the one final run.

## The families

### With a cause and a change before it (24)

| # | Family | Category | What happens | Before the failure |
|---|---|---|---|---|
| 1 | client_secret_double_encoded | authentication | A release URL-encodes the worker's client secret twice, so the partner's token endpoint answers `invalid_client` | Release (worker) |
| 2 | provider_rotated_signing_keys | authentication | The identity provider rotates its signing keys; the gateway still caches the old ones and rejects every token's signature | Partner alert |
| 3 | token_audience_changed | authentication | A release changes the audience the worker asks tokens for; the partner rejects them as issued for another audience | Release (worker) |
| 4 | role_removed_in_cleanup | authorisation | A permissions clean-up on the database removes the processor's write role; inserts fail with permission denied | Release (store) |
| 5 | egress_ip_changed | authorisation | A release moves the worker behind a new NAT gateway whose address isn't on the partner's allowlist; calls get 403 | Release (worker) |
| 6 | enum_value_added | schema_contract_mismatch | The processor starts sending a status value the worker's contract doesn't allow; messages are rejected | Release (processor) |
| 7 | list_became_object | schema_contract_mismatch | A gateway release sends a single item as an object instead of a one-item list; the processor rejects the type | Release (gateway) |
| 8 | firewall_rule_removed | networking | A network-policy change on the database stops the processor reaching it: no route to host | Release (store) |
| 9 | proxy_setting_added | networking | A release routes the worker's outbound calls through an internal proxy that can't reach the partner | Release (worker) |
| 10 | partner_degraded | timeout | The partner announces degraded performance; its responses take longer than the worker's 30-second limit | Partner alert |
| 11 | migration_locks_table | timeout | A schema migration on the database holds a table lock; the processor's writes wait and time out | Release (store) |
| 12 | retry_storm | rate_limiting | A release removes the worker's back-off; after a short blip, its retries exceed the partner's rate limit | Release (worker) |
| 13 | shared_key_new_consumer | rate_limiting | A new reports job starts using the worker's partner key, so they share one quota and the worker gets 429 | Release (reports), off the dependency path |
| 14 | timezone_shift | data_quality | A release stores order times in local time instead of UTC; daily reports put orders on the wrong day | Release (processor) |
| 15 | default_country_assumed | data_quality | A release fills a missing country with US; orders from elsewhere get the wrong tax | Release (gateway) |
| 16 | feed_migration_zero_prices | data_quality | After the partner migrates its price feed, some items arrive priced at 0 | Partner alert |
| 17 | truncated_upload | file_transfer | A release streams the export, and the transfer is cut at 60 seconds; the partner receives truncated files | Release (exporter) |
| 18 | filename_pattern_changed | file_transfer | A release adds a timestamp to export file names; the partner's pickup only matches the old pattern | Release (exporter) |
| 19 | consumer_group_renamed | queue_or_event_processing | A release renames the worker's consumer group; the new group starts at the latest offset, skipping messages | Release (worker) |
| 20 | visibility_timeout_shortened | queue_or_event_processing | A queue setting change makes messages visible again before the worker finishes; they're processed twice | Release (queue) |
| 21 | ordering_broken_by_concurrency | queue_or_event_processing | A release processes messages in parallel; an order's update arrives before its creation and is rejected | Release (worker) |
| 22 | wrong_image_tag | deployment_or_configuration | A release deploys a development image whose start-up flags don't exist in production; the processor won't start | Release (processor) |
| 23 | memory_limit_halved | deployment_or_configuration | A release halves the worker's memory limit; it's killed for running out of memory and restarts in a loop | Release (worker) |
| 24 | cron_schedule_typo | deployment_or_configuration | A release sets the reports job's schedule to the wrong hour, so the morning report is missing | Release (reports) |

### With a cause and nothing changed before it (8)

| # | Family | Category | What happens |
|---|---|---|---|
| 25 | clock_drift | authentication | The worker host's clock runs 7 minutes fast; the partner rejects its tokens as not yet valid |
| 26 | subscription_lapsed | authorisation | The partner account's subscription lapses; calls get 403 "subscription inactive" |
| 27 | partner_requires_new_field | schema_contract_mismatch | The partner's API starts requiring a currency field without notice; requests without it are rejected |
| 28 | certificate_expired | networking | The partner's TLS certificate expires; the worker's connections fail the handshake |
| 29 | table_outgrew_query | timeout | A table grows until a report query switches to a full scan and exceeds its 5-second limit |
| 30 | daily_quota_exhausted | rate_limiting | Month-end volume uses up the partner's daily quota by mid-afternoon; later calls get 429 |
| 31 | receiver_stopped_polling | file_transfer | The partner's pickup job stops polling; delivered files are never collected or acknowledged |
| 32 | poison_message | queue_or_event_processing | One malformed message fails and is retried forever, blocking its partition |

### No diagnosable cause (8)

| # | Family | What the evidence shows |
|---|---|---|
| 33 | sporadic_partner_502s | A few 502 responses from the partner over several hours, each succeeding on retry |
| 34 | one_slow_export | One night's export took three times as long; the next night was normal |
| 35 | scattered_401s | A handful of 401s over a day; the same tokens were accepted on retry |
| 36 | self_clearing_backlog | A short queue backlog that cleared by itself, with no rise in incoming messages |
| 37 | single_wrong_total | One customer reports a wrong total that the stored data doesn't reproduce |
| 38 | dns_blips | A few DNS lookup failures across services within one minute, then none |
| 39 | one_duplicate_notification | One customer got a notification twice; no other duplicates and no errors |
| 40 | late_report_once | The morning report finished 40 minutes late once, with no errors |

Every category with a cause has 3 or 4 families.

## Split

After the list is approved, a fixed seed (2031) assigns, in this order:
1. **Precedent:** half of each of the three groups above, at random.
2. **Development or test:** within each of the six resulting groups, at random, so that development gets 6 families with a change, 2 with nothing changed and 2 with no cause, and the test set gets the other 18, 6 and 6.

| Set | Families | Variants | Incidents | Use |
|---|---|---|---|---|
| Development | 10 | 5 | 50 | Any change to FlowGuard is made and checked here, alongside `data/benchmark-2028` |
| Test | 30 | 10 | 300 | Run once, after FlowGuard is frozen |

## Generated

On 2026-11-10, with `python -m flowguard.benchmark.generate_next --seed 2031 --out data/benchmark-2031`, from the families in `src/flowguard/benchmark/families_next.py`. The first generator and its families are unchanged, so the earlier sets can still be regenerated exactly.

| Set | Folder | Families | Incidents |
|---|---|---|---|
| Development | `data/benchmark-2031/dev` | 10: cron_schedule_typo, enum_value_added, feed_migration_zero_prices, retry_storm, role_removed_in_cleanup, visibility_timeout_shortened (a change); daily_quota_exhausted, table_outgrew_query (nothing changed); late_report_once, scattered_401s (no cause) | 50 |
| Test | `data/benchmark-2031/test` | The other 30 | 300 |

Half the families of each group in each set have a precedent. Development and test incidents are in separate folders, so a development run never retrieves a test family's documents. Each ground truth records its group and whether it has a precedent, so results can be broken down by both.

`python -m flowguard.benchmark.check` passes on both folders with the oracle, which answers from the ground truth and is not a model. For a cause with nothing changed before it, the rubric can't reach 0.65, so the checker requires the oracle to gather the required evidence and propose the right category, and validates the reference plan directly. The largest prompt is about 6,700 characters, well inside Gemma's context. No model has seen either folder.

## Development

The development set is for the next change to how FlowGuard decides. The probe on 2028 (brief, section 14) showed that reading only the symptoms names what failed but can't tell whether there's a cause, and that a change misleads in some families and explains the failure in others. So the change to develop lets Gemma use a change to explain the symptoms, instead of the rubric counting it or the probe hiding it.

It's built as the explain path (`src/flowguard/graph/nodes/explain.py`), switched on with `--diagnosis explain`, and off by default. Gemma answers two questions:

1. **What failed?** It sees only the symptoms (logs, API specs, the dependency map), describes the failure, says whether it is sustained or isolated, and names the category.
2. **What explains it?** It sees everything, including the changes and the documents, and says which change explains why the failure started, that no change is needed to explain it, or that nothing does.

Code decides: the reading must cite a log; an isolated failure, an unknown category, or an unexplained failure is an abstention; and after the second question the category may change only when a change explains the failure, and never to `deployment_or_configuration`, which the symptoms alone must show. The prompts were written from the category definitions and the probe's lessons. Their examples avoid the test families, though the person who wrote them also wrote those families.

Development runs, which are never reported as accuracy:

```powershell
conda run --no-capture-output -n flowguard python -m flowguard.evaluation.investigations --data-dir data/benchmark-2031/dev --split dev --output-dir reports/benchmark-2031-dev-rubric
conda run --no-capture-output -n flowguard python -m flowguard.evaluation.investigations --data-dir data/benchmark-2031/dev --split dev --diagnosis explain --output-dir reports/benchmark-2031-dev-explain
```

**Planned form of the test run, written before any development result.** Both the rubric and the explain path are frozen, then each runs once on the 300 test incidents. Reported for each: diagnosis accuracy on the 240 incidents with a cause, with the interval counted by family; abstention on the 60 without one; wrong diagnoses; and all three by group (a change, nothing changed, no cause) and by precedent. The marks that decide which becomes FlowGuard's default are written in the brief, with the frozen commit, before the test run.

**Development result 2026-11-10, never reported as accuracy.** Gemma on the 50 development incidents, with uncommitted code (commit 7c85dfa plus the working tree), in `reports/benchmark-2031-dev-rubric` and `reports/benchmark-2031-dev-explain`:

| Group | Rubric | Explain path |
|---|---|---|
| a change before the cause (30) | 23 right, 5 wrong, 2 abstained | 30 right |
| a cause with nothing changed (10) | 10 abstained | 10 right |
| no cause (10) | 10 abstained | 9 abstained, 1 wrong |

The rubric's 5 wrong took the trigger for the cause: a shortened visibility timeout read as a timeout (4), and zero prices from a migrated feed read as a schema mismatch (1). It abstained on every cause with nothing changed, as built. The explain path's one wrong was a `scattered_401s` variant in which every 401 was accepted on retry, which Gemma read as a sustained authentication failure. The explain path cited the change in 29 of the 30 incidents with one, and in none of the others. Precedent made no difference to it (15 of 15 right with and without). Both had 0 unsafe actions and 0 approval bypasses, and abstained on all 50 without logs. Its median time was 67 s against 51 s, and its plan recall 75% against 49%, mostly because more diagnoses were right. The prompts weren't changed after the run: with one miss in 50, a change would only fit that incident. The dev journal didn't record why each no-cause incident was abstained on; results now keep the abstention reason and the explain path's notes, such as which change it said explains the failure.

## The known gap the development set must address

With the rubric, a cause with nothing changed before it can't be diagnosed. Without a change, the best score is 0.55: an error log (0.30), an API spec (0.15) and a past incident (0.10). That's below the 0.65 bar, so FlowGuard abstains on every such incident by construction. The no-cause incidents have the same kinds of evidence, so a fix can't come from counting evidence kinds. It has to read what the evidence says, for example an error that names its cause ("certificate has expired"). The development set has 2 families of each kind for this work. If no fix holds up there, the test set reports the gap as it is: the 6 test families without a change would score close to 0.

## Fixed before the test run

**Recorded 2026-11-10, before any model has seen the test folder.** These terms are also in the brief (section 14).

- **Code.** Frozen at the commit that adds these terms, tagged `benchmark-2031-frozen`. The runner refuses the test split when `src/flowguard` or the data folder has uncommitted changes, and each report records its commit. A report from any other commit doesn't count.
- **Runs.** Gemma `gemma4:12b`, reasoning off, once each on `data/benchmark-2031/test`: the rubric, FlowGuard's default, and the explain path. An interrupted run may resume from its journal; a finished incident is never rerun.

```powershell
conda run --no-capture-output -n flowguard python -m flowguard.evaluation.investigations --data-dir data/benchmark-2031/test --split test --output-dir reports/benchmark-2031-test-rubric
conda run --no-capture-output -n flowguard python -m flowguard.evaluation.investigations --data-dir data/benchmark-2031/test --split test --diagnosis explain --output-dir reports/benchmark-2031-test-explain
```

- **Scoring.** The 300 incidents are in 30 families: 180 with a change before the cause (18 families), 60 with a cause and nothing changed (6) and 60 without a cause (6). An incident with a cause is right when FlowGuard names its category, wrong when it names another, and abstained otherwise. One without a cause is right when FlowGuard abstains, and wrong otherwise.
- **The marks.** The explain path becomes FlowGuard's default only if all five hold:
  1. Right on the 240 with a cause: at least 24 more than the rubric, ten points.
  2. Precision, right ÷ (right + wrong) over all 300: at least the rubric's.
  3. It abstains on at least 54 of the 60 without a cause.
  4. Right on the 180 with a change: no more than 9 fewer than the rubric, five points.
  5. In both runs: 0 unsafe actions, 0 approval bypasses, and an abstention on every incident when logs are denied.

  If any fails, the rubric stays the default and the explain path stays off.
- **Reported for both, whatever the outcome.** Diagnosis accuracy on the 240 with the Wilson interval and the interval counted by family, against the 80% target; abstention on the 60; wrong diagnoses; each by group and by precedent; plan recall, plan precision and change precision; unsafe actions, approval bypasses and latency. FlowGuard's accuracy is the default's, after the marks. The test set is then spent: never tuned on, never run again.

## Result

On 2026-11-11, from the tagged commit, the explain path diagnosed 206 of the 240 test incidents with a cause (86%) and abstained on 59 of the 60 without one; the rubric diagnosed 139 (58%) and abstained on all 60. Four marks passed; the precision mark was worded ambiguously, passing as the precision of the answers given and missing by 0.1 points read literally. The explain path became FlowGuard's default the same day. Claude Sonnet 5.5 then ran the explain path once on the same incidents, to compare a hosted model with Gemma: 217 right, 1 wrong and 22 abstained on the 240 with a cause, and all 60 without one abstained on. The details are in [`evaluation.md`](evaluation.md#benchmark-2031) and the brief, section 14.
