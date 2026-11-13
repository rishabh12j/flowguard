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

Eight is about twice the chance variation of a net difference over 12 disagreements. Clarified on 2026-11-13, before any part was measured: the lead agent is the base the other parts sit on, so its result against both baseline runs is recorded and it stays either way. Every later part is judged by these thresholds against the configuration it was added to (the survey against the lead's run, and so on). A part that doesn't qualify is removed, and the result is recorded either way. Each comparison costs about $3 to $6 on Haiku.

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

## Agreed by the user, 2026-11-13

The user agreed every point:

- **The design**, as written above.
- **The bar for the held-out test**, and the rule for keeping a part in phase 5.
- **The scorer's rule for optional faults:** a left-over claim naming one counts neither for nor against an answer.
- **That the agents may be told how the scoring code places a fault:** an HTTP fault at the calling service, a network fault at either end.

The standard agent is not told this placement rule, so every report of a comparison says that ours is.

## Phase 5, step 1: the lead agent and the survey, built 2026-11-13

Built and checked offline, then measured on 2026-11-13 (results below).

- **The agent.** `python -m flowguard.openrca2.baseline --agent lead|lead+survey` runs the design's first two parts with the same runner, tools, limits and records as the standard agent (`--agent standard`, the default). Each record notes its agent.
- **The lead** (`openrca2/design.py`) has the standard agent's four tools and its cap of 100 calls. Its own prompt says:
  - how answers are judged: the agreed placement rules, and that a fault is named only if its effect spread;
  - how to work: every service first, own work against inherited, silence, telling similar kinds apart, then the path to the users;
  - the official answer contract, from the first turn rather than only at the end.

  The answer turn keeps the same system prompt, so no history is edited: the model's thinking stays valid and the cache stays warm. The answer is held to the official schema by structured output, with the 25 kinds as a fixed list.
- **The survey** (`openrca2/survey.py`) is added to the first message. It holds:
  - every service's rates, error share, latency, own time, log errors, largest metric shift (and which metric), restarts, new pods and onset;
  - the calls between services that changed most;
  - the entry services: those taking at least 5% of the load generator's calls, or, with no load generator in the traces, starting at least 25% of the traces;
  - the network connections that changed most, where the case records them. Hubble metrics are in 46 of 60 TrainTicket development cases and in no Hotel Reservation or OTel Demo case; where they are absent, the survey says so.

  It takes under a second and about 1,000 to 3,500 tokens a case.
- **Tests** (`tests/unit/test_openrca2_design.py`):
  - the survey, on a synthetic case with a known entry service, a failing callee, restarts, a new pod and a doubled connection;
  - the lead's prompt and answer settings;
  - the answer turn replaying the history untouched and sending the schema;
  - the strict schema.

**Measuring it** costs about $3 to $4 a configuration on Haiku: the standard agent's cost, plus a few cents of survey tokens, less the answer turn's cache misses. Each configuration is first run on one case, to check that structured output works with Haiku in a real request.

### Results on the 100 development cases, 2026-11-13

Both configurations ran on all 100 development cases on Claude Haiku 5.5, after a one-case check each (case-073, exact in both). Structured output worked in every case. The full comparison, with every miss classed, is `reports/openrca2-phase5-step1-compared.md`.

| Run | Exact | Hotel Reservation | OTel Demo | TrainTicket | Cost |
|---|---|---|---|---|---|
| Standard agent, run 1 | 56 | 31 of 33 | 5 of 7 | 20 of 60 | $2.97 |
| Standard agent, run 2 | 56 | 32 of 33 | 7 of 7 | 17 of 60 | $3.23 |
| Lead | 50 | 22 of 33 | 4 of 7 | 24 of 60 | $5.06 |
| Lead and survey | 62 | 28 of 33 | 4 of 7 | 30 of 60 | $3.46 |

| Pair | Only the first right | Only the second right | Exact paired test |
|---|---|---|---|
| Standard run 1, lead | 19 | 13 | p = 0.38 |
| Standard run 2, lead | 18 | 12 | p = 0.36 |
| Lead, lead and survey | 5 | 17 | p = 0.017 |
| Standard run 1, lead and survey | 10 | 16 | p = 0.33 |
| Standard run 2, lead and survey | 9 | 15 | p = 0.31 |

**The lead, against both baseline runs (recorded; it stays as the base).** It is 6 exact matches worse, which is within the chance spread, but its losses fall on one system: Hotel Reservation drops from 31 and 32 to 22. Three things drive this:

- **The placement rule worked on HTTP faults.** Eight TrainTicket HTTP faults that both baseline runs blamed on the called service are now named at the caller and scored exact (case-073, 092, 165, 199, 256, 258, 270, 384).
- **The same rule turned network delays into HTTP faults.** A network delay on a service's own connections slows its outgoing calls while the called services' server spans stay normal. That is the pattern the prompt describes for an HTTP fault. The lead named `http_slow` for a network delay in 8 cases: 6 at Hotel Reservation's `search`, which both baseline runs got right, 1 in OTel Demo and 1 in TrainTicket.
- **Five answers were empty.** In 5 cases (267, 296, 352, 433, 442) the answer turn returned `{"root_causes": [], "propagation": []}`. In two of them (267 and 352), the lead's last think_tool note names the right service and kind. The other three runs have no empty answers. The cause is not known. All five had long histories at the answer turn (53K to 95K tokens), but so did most cases: 61 of the 100 were over 60K and were answered. An empty answer is never right: every case has at least one fault.

The lead also cost more than the baseline ($5.06 against about $3). Fifteen cases ran past 100K prompt tokens on a turn, where Haiku's price is five times higher; they cost 11 to 27 cents each.

**The survey, against the lead (kept).** It passes all three thresholds:

- 12 more exact matches (17 gained, 5 lost; p = 0.017);
- no system loses: Hotel Reservation +6, OTel Demo 0, TrainTicket +6;
- 3.5 cents a case.

Three of the 17 gains are cases where the lead's answer was empty (267, 352, 442). Without them the gain is 9 (14 against 5, p = 0.064). That still clears the threshold of 8, but the margin is thin. Where the survey helped:

- It undid most of the lead's network-delay misreads in Hotel Reservation (056, 065, 337, 391). It named the delay at the other end of the connection, which counts.
- It brought TrainTicket network faults to the right kind (120, 226, 300, 401).
- It shortened the investigations: 62.9M prompt tokens against the lead's 86.1M.

**Lead and survey, against the baseline (information only; the held-out test decides).** It is 6 exact matches ahead of both baseline runs (net +6 and +6, p about 0.3). That is not yet enough. The held-out bar was designed to detect a gain of about 4 to 5 points over 355 cases, so a 6-point gain on development is in range but not secure. Hotel Reservation is still 3 to 4 below the baseline. TrainTicket is 10 to 13 above.

**What the remaining 38 misses are.** Wrong kind is 31 of them:

- a network fault on a connection to MySQL read as `database_call_slow` or `database_call_failed`: 13;
- a network delay read as `http_slow`: 3;
- a network partition read as `dns_lookup_failed`: 2;
- `jvm_heap_exhausted` read as `pod_failure`: 3.

The rest are a wrong service (5), the entry service named instead (3) and a missed second fault (2). This is the list the kind subagent is aimed at.

### Open points for the user

1. **The empty answers.** There are two ways to stop the answer turn returning nothing:
   - `minItems: 1` on `root_causes` in the answer schema. It is free and certain. It also forces a guess where the model thinks there is no fault, but every case has one, and the official contract says so.
   - Rerun the answer turn once when it comes back empty. It keeps the schema as the official one and costs one more answer turn (about a cent) in the rare case. If the model's choice was deliberate, it may return empty again.

   I recommend `minItems: 1`. The task says every case has a fault, so it adds no assumption, and the fix belongs to the client, not the reasoning. Either way it applies to the lead and survey configuration, so the next comparison uses the fixed version as its base.
2. **Network delay against HTTP slowness at the caller.** The lead's rule for HTTP faults is right but incomplete: it says what an HTTP fault looks like, not what separates it from a delay on the caller's own network. I propose to put the separating evidence in the kind subagent's brief rather than change the lead prompt, which has already been measured. The evidence is whether every outgoing connection of the pod is slowed (any destination, any protocol, database included) or only particular HTTP routes.
