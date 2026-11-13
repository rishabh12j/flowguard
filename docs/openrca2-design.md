# OpenRCA 2.0: the proposed design

Phase 4 of the plan in `brief.md`, section 33. It says what code should do and what agents should do, why, what it costs, and the bars a design must pass. It is a proposal for review: nothing here is built until the user agrees. It rests on phases 1 to 3 (`docs/openrca2-task.md`, `docs/openrca2-data.md`, `docs/openrca2-baseline.md`), all on development cases only.

## What the design must answer

What is known about where points are won and lost:

1. **The answer is nearly always in the data, but no one view shows it** (phase 2). Some simple signal ranks the faulty service in its first three in 99 of 100 cases. The best single signal manages 60%, and which signal works depends on the kind of fault and on the system.
2. **Anomalous is not the same as required** (phase 2). Optional and not-effective faults look as anomalous as required ones. A fault is required when its effect spread beyond its own service, so the evidence to name a fault is spread, not loudness. Naming a not-effective fault breaks an exact match.
3. **The loudest wrong answer is usually downstream** (phase 2, and the paper). Entry services carry the errors and latency of what they call. The paper's other failure modes are related: an agent stops at the first plausible cause, reads a dead service's silence as normal, and names a service without a path to the symptom.
4. **The standard agent is already strong** (phase 3). On Claude Haiku 5.5 it made 7 exact matches in 10 cases, for about 3 cents and 70 seconds a case. Its misses were one wrong service (OTel Demo) and twice the same wrong kind: a network partition to the database read as failing database calls.
5. **The standard agent has costs a design can avoid.** It resends its whole history each turn (270K to 834K prompt tokens a case). It reads raw rows to find what code could summarise in milliseconds: the phase 2 study scored every service of 100 cases in 16 seconds.

## What the 100-case baseline showed

The user ran the standard agent on Claude Haiku 5.5 on all 100 development cases, twice (`reports/openrca2-baseline-haiku`, `-run2`; $2.97 and $3.23). The comparison is reproduced by `python -m flowguard.openrca2.failures` (`reports/openrca2-baseline-haiku-compared.md`).

**Exact match was 56 of 100 in both runs.** Under the public scorer's rule, every injected fault required, it was 38 and 35. The ten-case sample's 7 of 10 was a lucky draw.

**The spread between runs.** The runs agree on 88 cases: 50 right in both and 38 wrong in both. Twelve flip, six each way. A change to the agent has to win clearly more than that to be told from chance (the bars below).

**By system:**

| System | Run 1 | Run 2 |
|---|---|---|
| Hotel Reservation | 31 of 33 | 32 of 33 |
| OTel Demo | 5 of 7 | 7 of 7 |
| TrainTicket | 20 of 60 | 17 of 60 |

TrainTicket holds 40 and 43 of the 44 misses. It is also 215 of the 355 held-out cases.

**What the misses were**, per run of 44:

- **The wrong kind on the right service: 32 and 31 cases.** The largest group is a network fault on a service's link to MySQL called a database fault:
  - `network_loss`, `network_corrupt` or `network_delay` called `database_call_slow`: 11 and 10 times;
  - `network_partition` called `database_call_failed`: 3 and 5 times.

  Next come restarts misread: a killed pod (`pod_failure`) called CPU saturation, and JVM heap exhaustion called `pod_failure`, 5 to 6 times a run. The rest are scattered among the HTTP and network kinds.
- **The wrong service: 9 and 10 cases.** Most are HTTP faults blamed on the service being called instead of the caller. For example, `ts-preserve-service` with `http_aborted` was named as `ts-seat-service` or `ts-basic-service`, which it calls. The official scoring code counts an HTTP fault only at the caller, because the fault mechanism sits in the caller's pod. Its design note says most models make this mistake. The agent contract does not say it. (The failures report files these as "another service": the called service is not on the true graph, which runs from the fault toward the user.)
- **A second required fault missed:** 1 or 2 cases. **Invalid answers:** 1 per run.

**Is the network-or-database question answerable from the data?** In one development case of `network_loss` between `ts-price-service` and MySQL, the per-connection metric `hubble_flows_processed_total` rose about 65% in each direction on that pair. The same metric rose 8% on another service's link to MySQL, and not at all on the load generator's. Packet loss on one link shows as extra traffic on that link only, which a fault inside the JVM's database calls would not be expected to cause. The development set holds no true database-fault case to confirm this. So it is evidence for the agents to weigh, not a rule.

## The proposal

A lead agent that plans and concludes; subagents with fresh, short contexts that each answer one question; and code that surveys the telemetry and checks what the agents claim. This is the shape the user set at the start of the restart ("a main agent that sends questions to subagents and concludes on the root cause").

**1. Survey (code, no model).** Before any agent runs, code reads the case once and writes a compact survey:

- the call graph between services, taken from parent and child spans;
- the entry services, which have spans with no parent from another service;
- for every service, the phase 2 signals: error share, latency, own time, silence in traces and logs, error logs, and the largest metric shift;
- for every service, the minute its first deviation began;
- for every connection between two pods, how its network traffic changed (`hubble_flows_processed_total`, `hubble_tcp_flags_total`, `hubble_drop_total`). This is the evidence the network-or-database question needs;
- for every service, signs of a restart: a pod name that appears or disappears, a gap in its spans.

The survey covers every service, so nothing is missed because an agent never queried it, and the call graph is there from the first turn.

- *What it may not do:* rank or filter the answer. It is a hint, and the agents may name a service it shows as quiet. This is the RE3 lesson: the candidate rule there was a hard limit, and the answer was outside it in 27 of 60 cases.
- *What it costs:* code only, under a second a case.

**2. Lead agent (model).** It gets the incident text, the survey and the answer contract, and works through hypotheses:

- which services might be at fault, and as what kind;
- which question to send a subagent next;
- when the evidence is enough to answer.

It has the standard agent's SQL tool for its own checks. It writes the final answer, in the official schema, held by structured output, so it cannot lose a case to format.

**3. Subagents (model, a fresh context each).** Each gets one question, the part of the survey it needs, and the SQL tool. It returns a short verdict with its evidence queries, so the lead's context holds conclusions, not raw rows. Three kinds of question, one for each known way points are lost:

- **Origin:** "Did service X's own work go wrong, or did it inherit the failure from something it calls?" This works from its own time against its callees, error origin, and silence. It targets the downstream mistake and the silent dead service. For an HTTP fault it also decides caller or callee, from where the failure first shows: in the caller's client spans, with the callee's server spans unchanged.
- **Kind:** "Given what X shows, which kind of fault is it?" It is given the official disambiguation rules (the contract's own text, part of the task) and checks the evidence each rule names. For example, to tell a network partition from a failing database call, it checks whether X's other connections also fail. It targets the largest class of misses, in this order:
  - a network fault on a link against a fault in the database calls: the link's own traffic, and whether the peer's other connections are affected;
  - a restart against saturation: restart signs and the memory trend before them;
  - the HTTP kinds against each other and against network kinds.
- **Spread:** "Does the fault at X reach other services, and by which path to an entry service?" It returns the edges with evidence. It decides whether a fault is worth naming (required or not) and supplies the propagation graph that edge-F1 and path-acc score.

**4. Checker (code, no model).** Before the answer is final, code checks every claim:

- that each evidence query runs and returns rows;
- that each named service exists in the data;
- that each edge joins services that call each other in the traces, in either direction;
- that each named root reaches an entry service through the answer's edges.

Failures go back to the lead once, as a list of problems. The lead may still answer as it sees fit: the checker reports, it does not decide. This is "the model investigates; code checks" from section 33.

**Models.** Claude Haiku 5.5 for the lead and the subagents, the same model as the baseline, so a difference in score is the design's and not the model's. Local models play no part (phase 3).

## Trade-offs

| Choice | What it buys | What it costs or risks |
|---|---|---|
| Code survey | Every service seen from the first turn; the call graph without the agent rebuilding it; free and fast | The agents may anchor on it and stop looking past its top rows: the RE3 mistake in a softer form. Kept only if the ablation shows it helps. |
| Subagents with fresh contexts | Short contexts (cheaper per turn, less long-context degradation); questions aimed at known failure modes | Information lost in summaries between agents; more model calls; two multi-agent systems on OpenRCA 1.0 scored under 3% (brief, section 33) |
| Fixed question types | Each targets a measured failure | Ones not yet seen are not targeted; the full 100-case baseline may reorder priorities |
| Checker | Ungrounded answers caught by code, not by more model calls | Can only check form (queries run, edges exist), not whether the evidence supports the claim |
| Structured output for the answer | No case lost to format | None found; it is also what the baseline's local runs needed |
| Same model as the baseline | A fair comparison | A stronger model might gain more from the design, or less; not measured |

**Cost.** The lead's turns resend its history, but that history holds verdicts, not rows. Subagents start empty. A rough estimate, from the baseline's token profile: 300K to 800K prompt tokens a case, close to the baseline's, at 3 to 6 cents a case on Haiku. Phase 5 measures it.

**What is not proposed.**

- No learned model and no rules fitted to the labels. Thresholds learned from labelled cases would be fitting the benchmark; the authors' own thresholds were measured on cases that include the held-out ones.
- No use of the dataset's priors, such as `search` being the commonest root in Hotel Reservation.
- No reuse of the old FlowGuard pipeline. Its LangGraph workflow, MCP servers and retrieval were built for synthetic integration incidents. They stay in the repository, untouched; the new system lives in `src/flowguard/openrca2`.

## Phase 5: how each part earns its place

Built in this order, each run on all 100 development cases and compared case by case with both baseline runs:

1. **Lead agent alone**, with the SQL tool and structured output. This isolates what the prompt and structured output do.
2. **Plus the survey.**
3. **Plus the subagents**, one question type at a time.
4. **Plus the checker.**

**When a part stays.** Two identical baseline runs disagreed on 12 cases and tied on the total. So a part stays only if, against each baseline run:

- it has at least 8 more exact matches;
- no system loses more than 2;
- it costs no more than 10 cents a case.

Eight is about twice the chance variation of a net difference over 12 disagreements. A part that doesn't qualify is removed, and the result is recorded either way. Each comparison costs about $3 to $6 on Haiku.

Nothing is tuned on one system alone. Every change is reported per system, and a change that helps one system while hurting another is not kept on the strength of the first.

## The bars, fixed before phase 5

**The test.** One run of the final design and one run of the standard agent on the 355 held-out cases, both on Claude Haiku 5.5, scored by this project's scorer. Both scoring rules are reported: the roles from `label.json`, and the public scorer's rule that every injected fault is required.

- **Main measure:** exact match (the leaderboard's acc).
- **The design passes** if its exact match is higher than the standard agent's and an exact paired test on the cases where the two disagree gives p < 0.05.
- **Reported beside it:** f1, any-hit, all-hit, type-acc, node-F1, edge-F1, path-acc, cost and time per case, each system apart and together.
- **Cost:** about $11 for the standard agent (measured at about 3 cents a case) and an estimated $15 to $25 for the design.
- **What to expect.** On development cases the standard agent made 56% exact matches. With 355 cases, the paired test reaches p < 0.05 for a net gain of about 15 to 19 cases (4 to 5 points), depending on how often the two disagree: 43 disagreements if they disagree as often as two baseline runs do, around 70 if more. A smaller gain could be real and still fail the bar.

**The published rows** stay a reference, not the bar. They are on the older 500-case data, with other labels and other models. A claim to have beaten the leaderboard needs a submission under its own rules.

**Development target:** a version that beats the standard agent on the development cases by more than the run-to-run spread, before the held-out cases are run at all.

## What phase 4 still needs from the user

1. **Agree or change the design** above.
2. **Agree the bar** (the test section) and the rule for keeping a part in phase 5.
3. **Agree the scorer's rule for optional faults.** A left-over claim naming an optional fault counts neither for nor against an answer. It changed no score so far, but it will be fixed before the test.
4. **May the agents be told where the scoring code places a fault?** For HTTP faults, the fault is counted at the caller; for network faults, at either end. This is how the answer is judged, not a threshold fitted to labels; phase 1 proposed that the scoring rules are part of the task and may be used. The standard agent was not told it, so telling ours is an advantage the bar should know about. The alternative is to leave it to the agents to infer from the telemetry, which the origin question is built to do anyway.
