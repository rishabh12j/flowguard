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

### Decided by the user, 2026-11-13

1. **Empty answers:** `root_causes` now has `minItems: 1` in the answer schema (`openrca2/baseline.py`). It applies to every agent that answers by structured output. The lead and survey run had no empty answer, so its 62 stands as the base for the next comparison.
2. **Network delay against HTTP slowness:** the separating evidence goes in the kind subagent's brief. The lead prompt stays as measured.
3. **A check before the held-out test, added to the bar.** The keep rule judges each part against the configuration before it, so nothing so far compares the whole design with the standard agent system by system. Before the held-out test is run, the final design must be no more than 2 exact matches below each of the two baseline runs on every system, on the development cases. As measured, lead and survey fails this on Hotel Reservation (28, against 31 and 32). If the final design fails it, the design is fixed and measured again before any held-out case is run.

## Phase 5, step 2: the kind check, built 2026-11-13

Built and checked offline; not yet run on any case. The user chose, from the trade-offs set out before building: code sends every fault of the lead's draft for a check; the subagent is told the claimed kind and tries to disprove it; the lead has the last word.

- **Run with** `--agent lead+survey+kind`. The lead's prompt, survey and first answer are exactly those of `lead+survey`. A test checks this, so a change in score is the check's.
- **The flow:**
  1. The lead investigates and writes its answer, as before. This is now the draft.
  2. Code sends each fault in the draft, up to 3, to a kind subagent (`openrca2/subagents.py`). Each subagent starts in a fresh context.
  3. If every check agrees, the draft is the answer. If any disagrees, the lead is shown all the findings, told that the checker saw less of the case and can be wrong, and writes its final answer. The lead's history is kept, so its thinking and cache stay valid.
- **The subagent is given:**
  - the claim: the service, the kind and the lead's evidence;
  - the survey;
  - the same four tools, capped at 20 calls, with about 10 advised.

  Its system prompt holds three things:
  - the description of the tables, as the lead has it;
  - the contract's own definitions, boundary rules and equivalence classes, quoted, without the answer format;
  - a section on telling kinds apart by scope. Each family of fault acts at one level (a connection, particular HTTP requests, one method or statement, the whole pod, one resource), and that decides what it can touch and what it must leave alone.

  The section ends with the questions that separate the pairs confused most. It is written from how the faults work, not from particular cases, and it names no metric as required: a metric missing from a case proves nothing. The evidence that separates a network delay from HTTP slowness, as the user decided, is here.
- **Its finding** is held by structured output to a strict schema, in this order, so the reasoning is written before the verdict:
  1. the scope;
  2. the kinds ruled out, and why;
  3. the kind;
  4. the confidence;
  5. the evidence queries.

  Two kinds scored as the same answer count as agreement.
- **Failures don't lose a case:**
  - A check that fails or gives no usable finding is reported to the lead as such. If none disagrees, the draft stands.
  - A second answer that is invalid leaves the draft as the answer.
  - The spending limit covers the checks too. A check stops once the run's limit is reached.
- **Records.** Each case keeps the draft, the draft's scores, every check's finding, transcript and cost, and the final answer. `python -m flowguard.openrca2.failures` adds a table for such a run: how many drafts and final answers were exact, and how the answers moved where a check disagreed. So the check's effect can be read case by case, not just from the total.
- **Refactor.** The tool loop moved to `chat.explore`, shared by the lead and the subagent. `investigate` gives the same results as before for the other agents; their tests are unchanged and pass.

**The risk**, stated before measuring: a second opinion on the 62 drafts that are already right can talk the lead out of some of them. The report's table shows how many.

**Measuring it.** Each check adds about 0.5 to 1.5 cents: a 3,300-token system prompt, the survey, and about 10 calls with most of the history read from cache. The lead's second answer, when needed, adds under a cent. Expected cost: 4.5 to 6 cents a case, $5 to $7 for the 100 cases. It stays if, against lead and survey (62), it has at least 8 more exact matches, no system loses more than 2, and it costs at most 10 cents a case. Then the check before the held-out test also applies to whatever configuration is final.

## The plan to the end, agreed 2026-11-13

The user set a limit of $100 and 7 days from 2026-11-13. Within that, all remaining parts are built, in order of expected value, then the held-out test is run.

### Keep rules for the remaining parts, fixed before any of them is measured

Exact match cannot judge the remaining parts. The spread check and the checker mostly change the propagation edges, which exact match does not score. The origin check aims at about 10 remaining misses, too few to gain 8 net. So, agreed by the user:

| Part | It stays if, against the configuration it was added to |
|---|---|
| Kind check | at least 8 more exact matches; no system loses more than 2; at most 10 cents a case (the original rule) |
| Spread check | mean edge-F1 rises by at least 0.05; no fewer exact matches; no system loses more than 2 exact matches; at most 10 cents a case |
| Checker | the same as the spread check |
| Origin check | it fixes at least half of its target misses (another service named, the entry service named, a second fault missed) and breaks no more than 2 exact matches; at most 10 cents a case |

Edge-F1 is the mean over the cases whose graph is scored (95 of the 100). The comparison report now prints it for each run, and, for a run with checks, for the drafts and the final answers.

### The check before the held-out test

Unchanged from "Decided by the user, 2026-11-13": on the development cases, the final configuration must be no more than 2 exact matches below both baseline runs on every system. What to do if no configuration passes it by day 5 is left open, and will be asked only if it happens.

### Budget

| Item | Limit |
|---|---|
| Kind check, smoke test and 100 cases | $8 |
| Spread check, 100 cases | $8 |
| Checker, 100 cases | $8 |
| Origin check, 100 cases | $8 |
| Held-out test: the standard agent (about $12) and the final design (about $25), with retries; set aside first | $40 |
| Reserve: one repair run, or overruns | $28 |
| **Total** | **$100** |

Spent since 2026-11-13, when the limit was set: $24.18 (kind check smoke test $0.04, spread check smoke test $0.04, kind check 100 cases $5.10, standard agent on the fixed tool $3.18 from the reserve, spread check 100 cases $6.36, second kind check smoke test $0.03, second kind check 100 cases $4.57, third kind check 100 cases $4.86). Each run's `--max-usd` is set to its line here.

### Schedule

| Day | Runs | Work |
|---|---|---|
| 1 | Kind check | Spread check built |
| 2 | Spread check | Analysis; checker built |
| 3 | Checker | Analysis; origin check and the held-out runner built |
| 4 | Origin check | Analysis; the check before the held-out test; the final configuration chosen |
| 5 | Held-out test, both agents, split across terminals | |
| 6 | | Results and write-up |
| 7 | Spare | |

A part not measured by the end of day 4 is dropped, and recorded as not built. The held-out test starts on day 5 at the latest.

## Phase 5, step 3: the spread check, built 2026-11-13

Built and checked offline; not yet run on any case.

**What it targets.** On lead and survey, edge errors are almost all missing edges: 102 missed against 20 extra, and none reversed. Of the 59 exact cases with a scored graph, 13 still have edges that differ from the label's. In the cases read, the label counts every call link the effect travelled, toward the users. The lead gives one chain and stops. Two examples of what it leaves out:

- a direct call that skips a service on another route (TrainTicket: `ts-travel2-service` → `ts-ui-dashboard` beside the route through `ts-route-plan-service`);
- the other callees of a service whose network was at fault (Hotel Reservation: `geo` → `search` beside `rate` → `search`).

**How it works.** Run with `--agent lead+survey+spread`, or `--agent lead+survey+kind+spread` if the kind check is kept.

- **Routes, by code.** For each fault of the draft (up to 3), code lists the call links the fault's effect could travel. These are the links from the services the faulty service calls, then every caller route up to the entry services. Each link shows its calls a minute, error share and p95, normal against incident (`subagents.routes`, from the survey's call table). The list is a starting point, not a limit: the subagent is told to check it and that it may miss links.
- **The subagent** gets:
  - the fault;
  - the draft's edges;
  - the entry services;
  - the route list;
  - the survey;
  - the four tools, capped at 20 calls.

  Its system prompt holds the description of the tables, the contract's own rule for propagation edges (quoted) and how to judge a link. A link is an edge if the caller's calls to the called service changed in the incident. Every route counts, not only the first. A fault in a service's network or outgoing requests can touch all its connections. A link whose calls look normal is not an edge. A service that stopped passes nothing to the services it called.
- **Its finding** is held to a strict schema: its reasoning first, then the edges, each with a query showing the change on that link, then whether the effect reached the users.
- **The lead answers again** if any kind check disagrees, or if the edges found differ from the draft's. Service names are compared after lower-casing and removing hyphens and underscores. The lead is shown which found edges are new to its draft, and which of its draft's edges near the fault were not found. It has the last word, on faults and edges alike.
- **The kind check alone is unchanged:** with no spread check, the lead sees the same message as when the kind check is measured. A test checks this.
- **Failures don't lose a case:** a failed or unusable spread check leaves the draft as it is.

**Its cost:** a system prompt of about 700 tokens, a route list of 3 to 40 links, the survey, and about 10 calls. That's about 1 cent a fault. Because the found edges will often differ from the draft's, the lead answers again in most cases: under a cent each. Expected: 1.5 to 3 cents a case on top of the configuration it is added to, so $6 to $8 for 100 cases with the kind check, or $5 to $6 without it.

## Phase 5, step 2: the kind check, measured 2026-11-16

Run: `--agent lead+survey+kind`, Claude Haiku 5.5, the 100 development cases. Report: `reports/openrca2-phase5-step2-compared.md`.

| Run | Exact match | Hotel Reservation | OTel Demo | TrainTicket | Edge-F1 | Cost |
|---|---|---|---|---|---|---|
| Standard agent, run 1 | 56 | 31 of 33 | 5 of 7 | 20 of 60 | 0.827 | $2.97 |
| Standard agent, run 2 | 56 | 32 of 33 | 7 of 7 | 17 of 60 | 0.801 | $3.23 |
| Lead and survey | 62 | 28 | 4 | 30 | 0.891 | $3.46 |
| Lead and survey, this run's drafts | 60 | 24 | 5 | 31 | 0.855 | |
| Lead, survey and kind check | **72** | 25 | 4 | 43 | 0.858 | $5.10 |

**Against the keep rule, as written** (against the run of the configuration it was added to, lead and survey):

- exact matches: +10 (at least 8 needed): met. Paired: 19 cases only it got right, 9 only lead and survey got right, p = 0.087;
- no system loses more than 2: **not met**. Hotel Reservation 28 → 25 (−3); OTel Demo 4 → 4; TrainTicket 30 → 43;
- cost: 5.1 cents a case in all, of which the checks are 1.6 cents: met.

So by the rule as written, the kind check does not qualify, by one Hotel Reservation case.

**What the check itself did.** Each case keeps the lead's draft from before the check, so the check's own effect can be read on the same investigations. Draft 60, final 72: 16 drafts fixed, 4 broken, paired p = 0.012. By system: Hotel Reservation +1 (3 fixed, 2 broken), OTel Demo −1 (0 fixed, 1 broken), TrainTicket +12 (13 fixed, 1 broken). The Hotel Reservation loss against lead and survey comes from this run's drafts (24, against lead and survey's 28), before any check ran. Five of the Hotel Reservation cases that lead and survey got right and this run's drafts got wrong are the same miss: `search` named `http_slow` where the label is `network_delay` at `rate`, the confusion recorded in phase 5 step 1. On the same lead, the drafts' edge-F1 also fell from 0.891 to 0.855, so the lead's run-to-run spread is about 4 Hotel Reservation cases and 0.03 to 0.04 in edge-F1.

**How the misses changed.** The 13 network-to-database misreads of lead and survey (`network_loss`, `network_corrupt`, `network_partition` or `network_delay` read as `database_call_*`) are down to 2. The largest class now is a wrong member of the network family: `network_corrupt` → `network_loss` 5 times, `network_delay` → `network_loss` or `network_partition` 3 times, `network_partition` → `dns_lookup_failed` twice.

**The verdicts.** 112 checks on 100 cases; the lead answered again in 36.

- On a fault the draft had right (71 verdicts), the check agreed in 61 and disagreed in 10, 7 of them at low confidence. The lead took the check's kind in 7 of those 10 and kept its own in 3; 4 of the cases lost their exact match.
- On a fault the draft had wrong (35 verdicts), the check found the right kind in 18 and a different wrong kind in 17.
- 6 verdicts were on a service with no fault. No check failed or gave no finding.
- High-confidence verdicts were right in 19 of 20; low-confidence ones in 10 of 21.

**Decision, 2026-11-16: kept.** The rule as written says no, by one case; the within-run comparison says the check itself did not cost Hotel Reservation anything. The user kept it ("one miss from Hotel Reservation is bearable"). This is a judgement made after seeing the result, not a pass under the rule.

**The check before the held-out test, looking ahead.** On Hotel Reservation, every lead configuration measured is more than 2 below both baseline runs (lead and survey 28, this run 25, against 31 and 32). The Hotel Reservation miss is in the lead's drafts, not in any check, so a configuration that passes that check needs a change that reaches the lead's reading of `network_delay` against `http_slow`, or decision 2 will have to be asked.

## Decided by the user, 2026-11-16

1. **The kind check stays**, by the user's judgement after seeing the result (above). The configuration the next parts are added to is lead, survey and kind check.
2. **The time is 5 days from 2026-11-16**, so the cut-off of the earlier schedule no longer applies: the checker and the origin check are still built and measured. The $100 limit is unchanged.
3. **The spread check, and the checker after it, are judged within their own run**, against that run's drafts, not against another run. The same lead configuration scored 28 and then 24 on Hotel Reservation, and its drafts' edge-F1 moved from 0.891 to 0.855, so a run-to-run comparison is about as noisy as the effects being measured. Fixed before the spread check is measured:
   - **edge-F1:** the final answers' mean edge-F1 is at least 0.05 above the drafts'. For scale, the kind check alone moved it by 0.003 in its run;
   - **exact match:** on the cases where every kind check agreed with the draft, so that only the spread check could change the answer, the final answers have no fewer exact matches than the drafts, and no system loses more than 2;
   - **cost:** the spread checks cost at most 10 cents a case;
   - for information only, not a test: the final answers' exact matches against the kind check run's 72, which used the old tool.
4. **The tool failure is fixed.** See "The tool fix, 2026-11-16".

### The tool fix, 2026-11-16

Found while reading case-106 step by step. Three faults, all present in every run so far, the baselines included:

- **A query returning a time column failed.** DuckDB needs the `pytz` package to return a zoned timestamp, and the environment did not have it. In the baseline runs, 98 and 93 of the 100 cases had at least one such failed call, about 5% of all tool calls. The agents recovered by dropping the time column, at the cost of a turn and of the time order. Fixed: `pytz` is installed and listed in the `openrca2` extra.
- **Times followed the laptop's time zone.** The connection used the machine's zone, Asia/Calcutta (+05:30), so any time shown, and any hour or day bucket, was 5.5 hours off the data's UTC. Fixed: `CaseTelemetry.connect` sets the session to UTC, so results no longer depend on the machine. The survey uses `epoch` and minute buckets, which the offset does not move, so its values are unchanged.
- **The survey was not reproducible.** DuckDB returns groups in no fixed order, so rows that scored equally came out in a different order on each call, and where a list is cut (the 30 calls that changed most, the connections, a service's largest metric shift) which tied rows made the cut varied. On case-106, four calls gave four different texts; the values never differed. Fixed: the call and connection lists are sorted by name before the stable sorts, and a tie in the largest metric shift goes to the first metric name. Checked: 3 surveys each of 20 development cases, all identical.

Tests: a query returning a time column comes back in UTC, and the session zone is UTC (`test_openrca2_baseline.py`); a tie in the largest metric shift goes to the first name (`test_openrca2_design.py`; it records the rule, but passes on the old code too, so the 20-case check is what shows the fix).

**What it changes.** From the spread check's run on, the agents work with the fixed tool, and the held-out test will too. A comparison between a run on the fixed tool and one on the old tool mixes the tool's effect with the part's, which is a reason for judging the spread check within its own run (decision 3). The check before the held-out test compares the final configuration with the standard agent's runs, which used the old tool, so a third run of the standard agent on the fixed tool is proposed, for about $3.50 from the reserve.

### Schedule from 2026-11-16

| Day | Date | Runs | Work |
|---|---|---|---|
| 1 | 2026-11-16 | Spread check, split across two terminals; the standard agent on the fixed tool | Checker built |
| 2 | 2026-11-17 | Checker | Analysis; origin check built |
| 3 | 2026-11-18 | Origin check | Analysis; the check before the held-out test; the final configuration chosen; the held-out runner built |
| 4 | 2026-11-19 | Held-out test, both agents, split across terminals | |
| 5 | 2026-11-20 | | Results and write-up |

### The standard agent on the fixed tool, measured 2026-11-16

A third run of the standard agent, on the fixed tool. Report: `reports/openrca2-baseline-fixed-tool-compared.md`.

| Run | Tool | Exact match | Hotel Reservation | OTel Demo | TrainTicket | Edge-F1 | Failed tool calls | Cost |
|---|---|---|---|---|---|---|---|---|
| Standard agent, run 1 | old | 56 | 31 | 5 | 20 | 0.827 | 17.4% (196 for want of `pytz`) | $2.97 |
| Standard agent, run 2 | old | 56 | 32 | 7 | 17 | 0.801 | 15.8% (183) | $3.23 |
| Standard agent, run 3 | fixed | 54 | 30 | 4 | 20 | 0.836 | 11.1% (0) | $3.18 |

- **The fix did what it was for:** no call failed for want of `pytz`, and the share of failed calls fell from about 16% to 11%. The rest are the agent's own mistakes: wrong column names, results too big, SQL errors.
- **The score did not measurably move.** Run 3 against runs 1 and 2: 14 and 16 cases differ, split 6 to 8 and 7 to 9, p = 0.79 and 0.80, the same as the 12 that runs 1 and 2 differ on. So the comparisons between configurations made on the old tool stand, and the standard agent's held-out run, on the fixed tool, is a fair reference.
- **The check before the held-out test is unchanged.** It asks for no more than 2 below each baseline run on every system. Run 3 is not above runs 1 and 2 on any system, so the bars stay: Hotel Reservation 30 of 33, OTel Demo 5 of 7, TrainTicket 18 of 60. Lead, survey and kind check (25, 4, 43) are below the bar on Hotel Reservation by 5 and on OTel Demo by 1.

## Phase 5, step 3: the spread check, measured 2026-11-16

Run: `--agent lead+survey+kind+spread`, Claude Haiku 5.5, the 100 development cases, on the fixed tool, split across two terminals. Reports: `reports/openrca2-phase5-step3-spread-rule.md` (the keep rule) and `reports/openrca2-phase5-step3-compared.md`.

**Against the keep rule, fixed before the run** (final answers against the same run's drafts):

| Condition | Result | |
|---|---|---|
| Edge-F1 up by at least 0.05 (95 scored cases) | 0.871 → 0.905, **+0.035**. Hotel Reservation +0.011, OTel Demo +0.061, TrainTicket +0.044. Up in 20 cases, down in 4 | **not met** |
| On the 65 cases where every kind check agreed, no fewer exact matches; no system loses more than 2 | 55 → 55, no case moved | met |
| Spread checks at most 10 cents a case | 0.9 cents ($0.92); the whole run 6.4 cents ($6.36) | met |

**The spread check is not kept.** It added edges the drafts missed, as designed, and none of its 111 findings was unusable, but the gain is below the bar set before the run.

**It also seems to weaken the kind check.** For information (a different run, so not a test): this run's final answers have 66 exact matches, against 72 for the kind check's run, from drafts of 62 and 60. Within this run the kind check gained 4 (drafts 62, finals 66), against 12 in its own run. The verdicts were no worse; the lead took them less often:

| When the kind check disagreed with a wrong draft and was right | Kind check run | Kind and spread run |
|---|---|---|
| The lead took the check's kind | 16 | 9 |
| The lead kept its own | 2 | 6 |

The difference is not significant on its own (Fisher's exact p = 0.10), but four cases show it directly: case-125, case-154 and case-216 got the same verdict in both runs (`database_call_*` → `network_partition`), and so did case-056 (`http_slow` → `network_delay`). The lead took the verdict in the kind check's run and kept its draft in this one.

A likely cause, read from case-216 and case-125 and not tested: the spread check is briefed with the draft's kind, and its section of the lead's message is headed with it ("How the effect of `ts-station-service` (`database_call_failed`) travelled"). The lead then sees one investigator reject its kind and a second one apparently working from it, in a message about 13,000 characters long. The kind finding is no longer the only voice.

**Consequence.** The configuration stays lead, survey and kind check. The checker is added to it. If spread edges are tried again, the spread check should run after the kind check, use the kind the lead settles on (or none), and report in a separate step; that would be a new part, measured afresh.

**The check before the held-out test.** This run's Hotel Reservation (27) and OTel Demo (5) are nearer the bars (30 and 5) than the kind check's run (25 and 4), but the spread check is not kept, so they don't count toward it.

## The checker, sized before building, 2026-11-16

Before building the checker, its four checks were run by code on the final answers of lead, survey and kind check (the configuration it would join), with evidence re-graded on the fixed tool. Development cases only; no model was called. Script: the scratch `size_checker.py`, results below.

| Check | Fires on |
|---|---|
| An evidence query fails or returns no rows | 17 of 683 queries (16 empty, 1 error), in 11 cases |
| A named service is not in the data | none |
| An edge joins two services that never call each other | 2 of 303 edges, in 2 cases; neither is a label edge |
| A named root does not reach an entry service through the answer's edges | 4 cases, 3 of them already exact |
| **Any of these** | **17 cases, 14 of them already exact** |

- **It cannot reach its keep rule.** The rule asks for edge-F1 up by 0.05. Removing the 2 bad edges and completing the 4 short paths, even generously, adds about 0.02 over 95 cases. On exact match it could act on 3 cases that are wrong, while asking the lead to revisit 14 that are right.
- **The edge check would misfire on true edges.** 15 of the 384 label edges join services with no call between them in the traces, in either direction (for example a database with no spans of its own), so the check could only report, never remove.

So the checker, as designed, is not worth its run (about $5 to $6). Decision pending with the user.

**Where the remaining misses are instead.** Of the 11 Hotel Reservation and OTel Demo cases the configuration misses, 8 are the wrong kind within or into the network family: `network_delay` read as `network_loss`, `network_partition` or `http_slow` (5), `network_partition` read as `dns_lookup_failed` (2), `pod_unavailable` read as `network_partition` (1). The standard agent got most of them right in all three of its runs. Across systems, a wrong member of the network family is also the largest class on TrainTicket (`network_corrupt` read as `network_loss`, 5). When the kind check disagrees with the draft within the same family, it was right in none of 6 such verdicts over its two runs; across families it was right in 33 of 62.

## Network-fault study, 2026-11-16

**Why.** Of the 11 Hotel Reservation and OTel Demo cases that lead, survey and kind check miss, 8 are a wrong kind within or into the network family, and a wrong network member is also TrainTicket's largest miss class. The study asks how each network fault, and the kinds it is confused with, shows in the telemetry, measured by code at the true faulty service. Development cases only; the injection parameters in `answers/dev` were used to describe the faults, never shown to an agent. Scratch scripts: `net_inventory.py`, `net_study.py`, `net_table.py`, `net_signatures.py`.

**The faults.** Required faults in the 100 development cases:

| Kind | Cases | Systems | Injected |
|---|---|---|---|
| network_delay | 14 | Hotel Reservation 9, OTel Demo 2, TrainTicket 3 | 340 to 1,840 ms added, with jitter |
| network_partition | 10 | Hotel Reservation 2, TrainTicket 8 | all packets dropped |
| network_loss | 8 | TrainTicket only | 29% to 67% of packets lost |
| network_corrupt | 5 | TrainTicket only | 27% to 86% of packets corrupted |
| http_slow | 4 | TrainTicket only | |
| pod_unavailable | 29 | Hotel Reservation 22, OTel Demo 5, TrainTicket 2 | |
| dns_lookup_failed, database_call_slow, database_call_failed | 0 | | |

The agents name database and DNS faults; in the development cases they are never the answer.

**Four signatures**, measured on the faulty service's links (its own client calls, to the target where there is one, and its callers' calls into it, whichever moved more):

- **SHIFT:** the middle moved, p50 up by at least 100 ms, with errors at most 5%;
- **TAIL:** the middle barely moved (p50 up by less than 50 ms) but p95 rose by at least 150 ms, with errors at most 5%;
- **FAIL:** errors of at least 50%, or a p50 of at least 20 s (timeouts);
- **GONE:** the service has no spans and no logs in the incident.

| Kind | System | Cases | SHIFT | TAIL | FAIL | GONE | none |
|---|---|---|---|---|---|---|---|
| network_delay | Hotel Reservation | 9 | 9 | 0 | 0 | 0 | 0 |
| network_delay | OTel Demo | 2 | 2 | 0 | 0 | 0 | 0 |
| network_delay | TrainTicket | 3 | 3 | 0 | 0 | 0 | 0 |
| http_slow | TrainTicket | 4 | 2 | 3 | 0 | 0 | 0 |
| network_loss | TrainTicket | 8 | 5 | 5 | 0 | 0 | 2 |
| network_corrupt | TrainTicket | 5 | 2 | 4 | 0 | 0 | 0 |
| network_partition | Hotel Reservation | 2 | 0 | 0 | 2 | 0 | 0 |
| network_partition | TrainTicket | 8 | 0 | 0 | 3 | 1 | 4 |
| pod_unavailable | Hotel Reservation | 22 | 0 | 0 | 0 | 19 | 3 |
| pod_unavailable | OTel Demo | 5 | 0 | 0 | 0 | 3 | 2 |
| pod_unavailable | TrainTicket | 2 | 0 | 0 | 0 | 1 | 1 |
| pod_failure | TrainTicket | 8 | 0 | 2 | 0 | 0 | 6 |

**What the cases show**, read case by case:

1. **Delay moves the whole link, with no errors.** In all 14 delay cases, on all three systems, the calls over the faulty link became slower by about the injected latency (or a small multiple of it) at the 25th and 50th percentiles, not only at the 95th, and none failed. Where the called service is traced, its own server time did not change: the time went between the caller's span and the callee's. Every kind of traffic on the link slowed, gRPC calls and database queries included. In none of the 14 did the faulty link show a tail alone.
2. **Loss and corruption add a tail and leave most calls fast.** On the faulty link itself, the median rose by a few milliseconds while p95 rose to about 200, 400 or 600 ms, steps of TCP's retransmission timeout; errors stayed at zero unless loss was heavy (67%: errors and timeouts of minutes). The callers of a service that queries a database many times per request can show a raised median, because each request makes many calls. Loss and corruption look the same in every measure taken here: a corrupted packet fails its checksum and is retransmitted like a lost one. They occur only on TrainTicket in the development cases, so this rests on one system plus the mechanism.
3. **Partition makes calls fail, while the service lives.** On TrainTicket, calls over the partitioned link end at a timeout (30 s, 60 s, 130 s) with errors, and the service logs connection failures (`Communications link failure`, `Connection is not available`, timeouts). On Hotel Reservation, the caller's calls to the cut-off service fail at once (about 0.01 ms, every call) and the log says only that the call failed; nothing mentions DNS, yet the agent named `dns_lookup_failed` both times.
4. **A pod that is down disappears; a partitioned one does not.** In 23 of 29 `pod_unavailable` cases the service has no spans and no logs at all in the incident. On Hotel Reservation, callers' calls to a dead service also fail at once, exactly as in a partition; the difference is the service's own metrics. A dead pod's metrics fall to a few rows (448 → 24, 836 → 28, 392 → 22 in a period), while a partitioned pod's keep coming at their normal volume (682 → 488, 370 → 354). On TrainTicket, callers of a dead service log `connection refused`; callers of a partitioned one log timeouts.
5. **http_slow is not cleanly separated from delay** by these measures: it shows a raised median on two of its four cases and a tail on three. In the development cases it occurs only on TrainTicket, on HTTP calls, while delay also slows gRPC calls and database queries.

**What it means for the kind check.** Of the 8 Hotel Reservation and OTel Demo kind misses, the evidence in the telemetry points to the true kind in 7: four delays called loss, partition or http_slow (SHIFT with no errors and no tail), two partitions called DNS (instant failures, the target's metrics alive, no name-resolution error), and one unavailable pod called a partition (case-059: no spans and no logs at all). The OTel Demo delay called `http_slow` is an HTTP call and stays ambiguous. TrainTicket's `network_corrupt` called `network_loss` cannot be fixed from this telemetry.

### Decided by the user, 2026-11-16: the kind check, second version

Build both parts: (1) correct the kind check's brief with the measured signatures, and (2) give the kind check a table, computed by code, of the claimed service's calls and of whether each end is still alive. The lead, the survey and the review the lead receives are unchanged. It runs as `--agent lead+survey+kind2`; `lead+survey+kind` stays as it was measured.

**Keep rule, fixed before the run.** The second version replaces the first if its run on the 100 development cases has at least 72 exact matches (the first version's run) and no system more than 2 below that run (Hotel Reservation at least 23, OTel Demo at least 2, TrainTicket at least 41). The check before the held-out test (Hotel Reservation at least 30, OTel Demo at least 5, TrainTicket at least 18) is reported alongside it.

## Phase 5, step 4: the kind check, second version, built 2026-11-16

Built and checked offline; not yet run on any case. Run with `--agent lead+survey+kind2`. The lead, the survey, the answer turns and the review the lead receives are those of `lead+survey+kind`.

**1. The brief** (`subagents.KIND_SYSTEM_V2`) is the first version's with four passages replaced, and the code refuses to build it if any of them has changed:

- the network kinds, as the study measured them: delay moves the 25th and 50th percentiles as much as the 95th, with nothing failing; loss and corruption leave the median nearly where it was and add a tail in steps of about 200 ms, and cannot be told apart; a partition makes calls fail, at once or at a timeout, while both ends stay alive. (The first version said loss and corruption cause "timeouts, resets, connection errors" and a partition leaves calls "hanging until a timeout".)
- the pod kinds: `pod_unavailable` loses its spans and logs, and usually its metrics; `pod_failure` is a kill and restart.
- DNS: calls failing at once without name-resolution text are not evidence of DNS.
- two new questions for the pairs it confused: slow calls with nothing failing (delay against loss or corruption, keeping the claimed one of loss and corruption), and calls that fail (partition, a pod that is gone, or DNS).

**2. The call table** (`survey.shapes`), computed by code for the claimed service and put in the check's first message, before the survey:

- each operation a caller sends to a called service, with the claimed service at either end: calls a minute, error share, the caller's p25, p50 and p95, and the called service's own p50, normal against incident; the 12 rows that changed most;
- where no Server span answered a call, the called service is taken from the same caller's same operation elsewhere in the case when that names one service only (a gRPC method to a service gone silent), and otherwise shown as no traced callee;
- for the claimed service and up to 7 services on those rows: spans, logs and metric rows a minute, normal against incident.

It gives numbers only and names no kind. On the development cases, for every fault of the first version's 100 drafts (112), it built without error in at most 0.6 s, at most 2,900 characters (about 700 tokens).

**Tests:** the second version's brief holds the new passages and keeps the rest; the first version is unchanged without the table; a hand-built partition (every call failing at once, the callee silent in spans and logs but not in metrics) reads as such in the table, with the callee inferred.

## Phase 5, step 4: the kind check, second version, measured 2026-11-16

`--agent lead+survey+kind2` on the 100 development cases: 71 exact, $4.57 (4.6 cents a case, $1.38 of it the checks). Per case: `reports/openrca2-lead-survey-kind2/`.

| System (cases) | Lead and survey | First version: drafts → finals | Second version: drafts → finals | Spread run | Standard agent, fixed tool |
|---|---|---|---|---|---|
| Hotel Reservation (33) | 28 | 24 → 25 | 28 → **31** | 27 | 30 |
| OTel Demo (7) | 4 | 5 → 4 | 3 → **6** | 5 | 4 |
| TrainTicket (60) | 30 | 31 → 43 | 29 → **34** | 34 | 20 |
| All (100) | 62 | 60 → 72 | 60 → **71** | 66 | 54 |

**Keep rule: not met.** It asked for at least 72 exact and TrainTicket at least 41; the run has 71 and 34. By the rule, the first version stays.

**The check before the held-out test: met, for the first time.** Hotel Reservation 31 (bar 30), OTel Demo 6 (bar 5), TrainTicket 18 (bar 18, run has 34). The first version's run fails it on Hotel Reservation (25) and OTel Demo (4).

**Against the first version, case by case:** 11 won, 12 lost (p = 1.0). Overall the two runs cannot be told apart; they differ in where they are right.

**What the check did within its run:** drafts 60 → finals 72 in the first version (16 fixed, 4 broken), 60 → 71 in the second (16 fixed, 5 broken). Its verdicts, where they disagreed with the draft on a true fault's service:

| | First version | Second version |
|---|---|---|
| Draft wrong, verdict right | 18 (lead took 16) | 21 (lead took 14) |
| Draft right, verdict wrong | 10 (lead took 5) | 6 (lead took 5) |
| Both wrong | 7 | 9 |

The second version's verdicts are better (21 right corrections against 6 wrong ones, from 18 against 10), and the network study's targets moved as intended: the Hotel Reservation and OTel Demo delays called `http_slow` became `network_delay` (case-126, 155, 194, 434), a partition read as a dead pod became a partition (case-311), and DNS claims for a dead pod's callers were dropped (case-171, 398). Two things took TrainTicket's gain away:

1. **HTTP faults read as network faults.** True HTTP faults given a network verdict: 3 in the first version, 5 in the second. Four broke right drafts: `http_slow` → `network_delay` (case-387, 442), `http_aborted` → `network_partition` (case-092), `http_response_body_corrupted` → `network_corrupt` (case-256). The study described only the network kinds; an HTTP fault injected on one endpoint also slows every call to it, or fails it, so the new shapes fit it too. The brief's existing delay-against-HTTP passage was kept, but the new shapes seem to outweigh it.
2. **The lead kept its draft against right verdicts.** In four TrainTicket cases where a database call failed or slowed because of the network to MySQL (case-125, 216, 274, 339), both versions' checks concluded the same network kind with the same evidence (connection-level JDBC errors, no SQL-layer exception, MySQL serving the other services), and at the same confidence or higher in the second version. The lead took the verdict in all four in the first run and in none of the four in the second. The lead's reasoning is redacted in the transcript, so why is not known. If it were chance at the rate the lead keeps right verdicts overall, four of four would happen about 1 time in 100.

Run-to-run noise is large: the lead's drafts, the same configuration before any check, scored 24 and 28 on Hotel Reservation in the two runs. Of the second version's 6-case lead on Hotel Reservation, 4 are in the drafts.

**Open for the user.** The keep rule keeps the first version; the check before the held-out test passes only with the second. This is the situation decision 2 was left open for.

### Decided by the user, 2026-11-16: one more try, the third version

The user chose to try a third version quickly and then finish, since this work was added to the plan. It is judged by the second version's keep rule, against the first version's run: at least 72 exact, Hotel Reservation at least 23, OTel Demo at least 2, TrainTicket at least 41. The check before the held-out test is reported alongside. If it falls short, the user chooses between the first and the second version.

## HTTP-fault study, 2026-11-16

On the development cases, by code: each required HTTP fault (16, all on TrainTicket) and each delay and partition, on the link the injection names (caller to called service, from `injection.json`). An HTTP fault is injected for one method and route from one caller to one called service; a network fault for one connection (source to target), under every protocol on it. Most TrainTicket links carry a single route, so whether other routes on the link moved can decide only 3 of the 16.

| Kind | Cases | On the faulty link | The caller's error log |
|---|---|---|---|
| `http_slow` | 4 | p25, p50 and p95 all up by the injected delay to within about 2% (+2303 ms gives 2324, 2326, 2388); spread unchanged; no errors | none |
| `network_delay`, Hotel Reservation and TrainTicket | 10 | spread widens with the jitter: p95 well above p50 (TrainTicket 1210 / 1420 / 3132; 355 / 916 / 5752) | none |
| `network_delay`, OTel Demo | 2 | narrow, like `http_slow` (442 / 442 / 443) | none |
| `http_aborted` | 3 | fail in about 1 ms with no Server span, or at the called service's usual time | `Unexpected end of file from server` |
| `network_partition`, TrainTicket service links | 2 | hang about 130 s, then fail | `Connection timed out` |
| `http_wrong_status_code` | 3 | the called service answered as usual | an HTTP status error (`401 Unauthorized`) |
| `http_response_body_corrupted` | 6 | the called service answered fast | `HttpMessageNotReadableException`, a 405, a null pointer later |

A narrow, fixed shift does not separate `http_slow` from every delay (OTel Demo's delays are narrow too), but a widening spread separates a delay from `http_slow`. Failures at once with an early end of response are `http_aborted`, not a TrainTicket partition. Unreadable responses come from the application layer: corruption on the network is retransmitted and never reaches the application.

## Phase 5, step 5: the kind check, third version, built 2026-11-16

`--agent lead+survey+kind3`: the second version (brief and call table) with one more question in the brief, *An HTTP fault or a network fault?*, giving the four HTTP kinds' shapes from the study above (`subagents.KIND_SYSTEM_V3`, about 400 tokens more). The lead, the survey, the call table and the review the lead receives are unchanged. It does not address the lead keeping its draft against right verdicts.

## Decided by the user, 2026-11-16: the plan to the end

The origin check is not built. Sized on the development runs, it could help only where the lead names the wrong service: of the kind check's 28 misses, 4 miss a required service and 4 add a wrong one (second version: 4 and 2 of 29); the other 20 to 23 are a wrong kind. That is at most 6 to 8 cases, against a keep bar of 8.

| When | What |
|---|---|
| 2026-11-16 | The held-out runner built, while the third version runs |
| When the third version's run ends | Judged against its keep rule; the final configuration chosen; the check before the held-out test reported |
| 2026-11-17 | The held-out test: the standard agent and the final configuration |
| Then | Results and write-up |

## The held-out runner, built 2026-11-16

Built and tested on made-up cases only. No held-out case has been opened, listed or run.

- **Answering, blind:** `python -m flowguard.openrca2.baseline --held-out --shard k/n ...` answers every held-out case (from `split.json`), every n-th one from the k-th in each terminal. It opens the held-out telemetry with `final_test=True` and reads no answer: each record has its answer, draft, checks and transcript, and no scores. A held-out case cannot be named with `--cases` or drawn with `--sample`; held-out cases go only as the whole split. A case that fails is retried by running the same command again, which skips the cases already done.
- **Scoring, once, at the end:** `python -m flowguard.openrca2.final --standard ... --design ...` refuses to score until both runs have answered every held-out case (or `--count-missing-as-wrong` is given after retries have failed). It then reads the held-out answers, scores each saved answer and draft with the same scorer, and writes the comparison: exact matches and F1 by system, and the paired sign test against the bar agreed on 2026-11-13 (more exact matches than the standard agent, p < 0.05).
- **Scoring later is the same as scoring at once:** on the four development runs of 100 cases, scoring each saved answer again gave the runner's own scores in 400 of 400 cases, and the drafts' in every case that has one.

**Cost, estimated from the development runs:** the standard agent about 3.2 cents a case and the kind-check configurations 4.6 to 5.1 cents; on 355 cases about $11 and $18, $29 in all, within the $40 set aside. Each terminal's `--max-usd` is set so the caps add up to no more than $40.

## Phase 5, step 5: the kind check, third version, measured 2026-11-16

`--agent lead+survey+kind3` on the 100 development cases: 71 exact, $4.86 (4.9 cents a case, 2.3 minutes). Per case: `reports/openrca2-lead-survey-kind3/`.

| System (cases) | First version: drafts → finals | Second version: drafts → finals | Third version: drafts → finals | Standard agent, fixed tool |
|---|---|---|---|---|
| Hotel Reservation (33) | 24 → 25 | 28 → 31 | 26 → **29** | 30 |
| OTel Demo (7) | 5 → 4 | 3 → 6 | 6 → **3** | 4 |
| TrainTicket (60) | 31 → 43 | 29 → 34 | 33 → **39** | 20 |
| All (100) | 60 → 72 | 60 → 71 | 65 → **71** | 54 |

**Keep rule: not met.** It asked for at least 72 exact and TrainTicket at least 41; the run has 71 and 39.

**The check before the held-out test: not met.** Hotel Reservation 29 (bar 30) and OTel Demo 3 (bar 5).

**Case by case:** against the first version 10 won, 11 lost; against the second 9 won, 9 lost (p = 1.0 both). Against the standard agent 21 won, 4 lost (p = 0.001).

**What the new question did.** On the 16 cases with a required HTTP fault (all TrainTicket), the finals were right in 14 (first version), 9 (second) and 15 (third): the confusion it was built for is gone, and in no HTTP case did the check break a right draft. The run's TrainTicket losses against the first version are elsewhere: of the 8, 6 had a wrong draft the check did not correct (a network fault to MySQL or between services drafted as a slow or failed database call, in case-125, 146, 274, 296 and 339), one was a right draft (`pod_unavailable`, case-106) the check turned into a partition, and one blamed the wrong service. In OTel Demo the check broke 3 right drafts.

**Three runs, one total.** Three versions of the check scored 72, 71 and 71, and no pair differs case by case (p = 1.0). Per system they swing far more: TrainTicket 43, 34, 39 and Hotel Reservation 25, 31, 29. The drafts, written before any check by the same lead with the same survey, already range 24 to 28 on Hotel Reservation and 29 to 33 on TrainTicket. So one run's per-system count is a noisy reading, and the check before the held-out test, applied to a single run, can pass or fail on the same configuration.

**Open for the user, as decided:** the third version falls short, so the first version (72; fails the check before the held-out test on Hotel Reservation and OTel Demo) or the second (71; passes it) goes to the held-out test.

## Decided by the user, 2026-11-16: the second version goes to the held-out test

The final configuration is `--agent lead+survey+kind2`: the only one to pass the check before the held-out test, level with the first version overall (71 against 72, p = 1.0), with the fewest cases lost to the standard agent (2) and the lowest cost. Known weakness, from the development cases: it read HTTP faults as network faults (9 of 16 HTTP-fault cases right, against 14 and 15 for the other versions).

**The held-out test, 2026-11-17.** Both runs answer all 355 held-out cases blind, in shards that start together in fresh folders; then `flowguard.openrca2.final` scores both once and applies the bar.

| Run | Agent | Shards | `--max-usd` per shard | Estimate |
|---|---|---|---|---|
| Standard agent | `standard` | 2 | $7 | about $11, about 3.5 h |
| Final design | `lead+survey+kind2` | 4 | $5.50 | about $16, about 3.5 h |
| **Caps in all** | | | **$36**, within the $40 set aside | about $28 |

Each terminal counts what its folder had spent when it started, so a shard started late, or a retry of failed cases, is given the folder's whole cap ($14 for the standard agent, $22 for the design) and stops when the folder reaches it.
