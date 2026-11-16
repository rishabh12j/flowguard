# OpenRCA 2.0: the standard agent, rebuilt to measure it

Phase 3 of the plan in `brief.md`, section 33. The question is what the leaderboard's standard agent costs per case and where it fails, and whether a local model has any role. This note covers the rebuild and how it was checked. Results are added once the runs are done.

## What was rebuilt

`python -m flowguard.openrca2.baseline` is the leaderboard's agent as published, not a design of this project.

- **The loop.** One model calls four tools: list the tables, read a table's columns, run a SQL query, and write a note to itself. When it stops calling tools, or reaches 100 calls, one more call with a different system prompt turns the whole history into the JSON answer.
- **Prompts.** The paper's appendix F.4, word for word, with the reflection prompt the co-author's adaptation adds. The incident text is the official SDK's template, the same for every case.
- **The answer contract.** The official SDK's text (`src/flowguard/openrca2/prompts/agent_contract.md`): the JSON format, the 25 kinds of fault, and the rules for telling similar kinds apart. It was assembled from the SDK's files at commit `979ae70` and is not edited.
- **Tools.** The co-author's adaptation (`github.com/QishengLu/rca_study_thinkdepthai`, commit `26b5166`):
  - dots in column names become underscores;
  - a query returns 10 rows unless it asks for more;
  - a result over about 5,000 tokens is refused with advice to filter or aggregate;
  - an error message carries no file path.

  The tools run on the locked connection, so a query can read the case's ten tables and nothing else.
- **What a run records**, for every case: the tool calls, each turn's prompt and output tokens, the cost, the time, why the investigation ended, the answer, the scores, the status of each evidence query (as the official judge grades it), and the full transcript. A run refuses held-out cases. A paid run needs a spending limit, and stops when it is reached.
- **Models.** Claude goes through the Anthropic SDK with automatic prompt caching, so the history already sent is billed at the cache-read price. Local models go through Ollama.

## Known differences from the leaderboard's runs

- **The harness is not public**, so the exact message flow around the prompts is the closest reading of the paper and the co-author's code.
- **Temperature.** The current Claude Haiku and Sonnet models refuse any temperature but the default, so the paper's 0.7 is used only on local models. Thinking and effort are left at each model's defaults.
- **Tables.** All ten tables can be queried in every call. The co-author's tool mounts only the tables a call names.
- **The tool, before 2026-11-16.** Every run before that date lacked the `pytz` package, so a query returning a time column failed (about 5% of tool calls), and its times followed the laptop's zone (+05:30) instead of UTC. Both are fixed from 2026-11-16 (`docs/openrca2-design.md`, "The tool fix, 2026-11-16"); the leaderboard's runs are unlikely to have had either fault.
- **Evidence grading.** The official judge mounts the tables with their original column names, while the tools show underscores. An evidence query written as the tools taught would fail there. Here evidence queries are graded on the underscored tables the agent saw. SQL Exec is not a leaderboard column.

## Checks

- **With a scripted model** (`tests/unit/test_openrca2_baseline.py`, no model called):
  - the loop, the cap and the refusal of calls past it;
  - the spending limit;
  - reading a fenced or broken answer;
  - the tools' columns, row limit, size refusal and file references;
  - that a query cannot reach an answer file or reveal a path;
  - evidence grading, the fixed sample, and the Claude price arithmetic.
- **Locally**, on one development case with `gpt-oss:20b`. With the cap at 6 calls the whole path ran: 7 turns, 26K prompt tokens, about 2 minutes. At the answer turn the model asked for another tool instead of answering, although that turn offers none. The paper's harness would score this as an invalid answer, so the run records it as a note and scores it 0.

## The ten development cases

Drawn by `sample()` with seed `20261112`, in proportion to the systems: TrainTicket `case-073`, `case-095`, `case-117`, `case-216`, `case-237`, `case-274`; Hotel Reservation `case-036`, `case-164`, `case-352`; OTel Demo `case-155`.

## How a case's cost grows, measured locally

A second local run on the same case, capped at 20 calls, answered validly. It named the right service with the wrong kind and two extra services: any-hit 1, f1 0, node-F1 0.8, edge-F1 0.67. All 5 of its evidence queries ran.

- **How the history grew.** The prompt grew from 1,308 tokens on the first turn to 15,483 on the answer turn, about 700 tokens per tool call. A tool result averaged about 1,500 characters. The 21 turns sent 117,526 prompt tokens and received 3,822 output tokens, in 253 seconds.
- **The quadratic part.** The whole history is resent every turn, so prompt tokens grow with the square of the number of calls: about 1M for 50 calls and 3.7M at the cap of 100.
- **The local model's context.** A 50-call case ends with a history of about 37K tokens on `gpt-oss:20b`, and about 75K at the cap of 100. This note first said a context above 32K was not possible on the laptop; that was not measured, and it was wrong. Measured with Ollama's defaults, the model loads at 32K (62% of it on the CPU), 64K (68%) and its maximum of 128K (78%, with 2 GB of RAM still free), because its sliding-window attention keeps the cache small. Local runs now default to 128K, which holds a whole case. More of the model on the CPU makes each turn slower. If a prompt still comes near the limit, the run records a note on that turn.

## Cost estimate for ten development cases

Prompt caching bills the resent history at the cache-read price. Writes come to about the final history size; the answer turn's new system prompt is one full write. Output is taken at about 500 tokens a turn, thinking included. Ranges run from about 50 calls a case to the cap of 100, plus 35% for Claude's tokenizer counting more than `gpt-oss`'s.

| Model | Per case | Ten cases | Leaderboard row (old 500-case data) |
|---|---|---|---|
| Claude Haiku 5.5 | $0.04 to $0.11 | $0.40 to $1.20 | none |
| Claude Sonnet 5.5 | $0.60 to $1.75 | $6 to $18 | none |
| Claude Sonnet 5 | $0.70 to $2.25 | $7 to $23 | acc 27.20%, f1 43.20% |
| Claude Opus 5.5 | $1.20 to $3.50 | $12 to $35 | none |
| gpt-oss:20b, local, 128K context | $0, about 15 to 40 minutes | about 3 to 6 hours | none |

The estimate does not cover a model that makes several calls per turn (fewer turns, so cheaper) or results near the 5,000-token cap (more tokens, so dearer). Every paid run carries `--max-usd`, which stops it at that sum, so the estimate guides the choice of model and the limit enforces the budget.

## The first paid run failed on the history check, 2026-11-12

The user's first run used Claude Sonnet 5.5 with a $5 limit. All three cases it reached failed on their second request with a 400: the first answer's thinking block at `messages.1.content.8` (`content.4` in one case) was "bound to a different conversation". The user stopped the run. No case was scored, and the spend was one successful request per case.

- **The check.** On current Claude models a thinking block is bound to the system prompt, the tool list and every earlier message. Replaying it after any of these changed is refused, on accounts created since 2026-08-31.
- **The cause is not yet pinned down.** The client sent back the SDK's parsed blocks rather than the response as it came over the wire. Offline tests showed the round trip keeping unknown fields and non-ASCII text, so it is not proven to be the cause. The API's error ends with a sentence naming the first message that changed, but the client cut errors at 300 characters, which removed it.
- **A second fault.** It would have failed every case at the answer turn. That turn, as the paper runs it, has its own system prompt, which this check treats as an edit.

**What changed:**

- Responses are now kept and sent back exactly as they came over the wire.
- The answer turn is sent with every thinking block removed. Nothing is replayed, so nothing is checked. The paper runs it as a separate call anyway. The investigation turns are untouched.
- Errors keep their full text, plus the API's `anthropic-thinking-prefix-mismatch` header when it sends one.
- `--thinking-check error|drop_block` sends the thinking-binding controls and records each response's `input_transformations`. `--capture DIR` writes every request body, for the reference's `prefix_diff.py`.
- A failed case is recorded in `failed-<case>.json` with what it cost, so the spending limit counts it. It is tried again on the next run.

These are checked offline against a fake transport (`tests/unit/test_openrca2_chat_claude.py`). Whether they cure the 400 can only be shown by a request to the API.

## The probe after the fix

One development case (`case-073`) on Claude Sonnet 5.5, capped at 6 calls and $0.50, with `--thinking-check drop_block` and every request captured. It cost $0.115.

- **The check passed.** No response reported an `input_transformation`. The reference's `prefix_diff.py` found requests 1 to 4 identical in everything a thinking block is bound to, including one turn that replayed a thinking block. Request 5, the answer turn, has the new system prompt and replays no thinking, as intended. The original failure came in a turn holding nine or more blocks, so a full case is a stronger test. The ten-case run uses `--thinking-check error`, which fails loudly if the problem comes back.
- **The answer.** It named the right service (`ts-preserve-service`) and the right edge to `ts-ui-dashboard`, giving node-F1 1, edge-F1 1 and any-hit 1. It called the kind `network_delay`, where the truth is `http_response_body_corrupted`, so f1, acc and path-acc (which needs a hit) are 0. `gpt-oss:20b` had named the same service, as `application_exception`. Both lost the case on the kind of fault alone.
- **Sonnet's history grows faster than the local model's.** It made several calls per turn and asked for bigger results: 5 turns took the prompt from 2.5K to 19.4K tokens, about 2.8K a call against `gpt-oss`'s 700. Most of the prompt was billed as cache writes or reads (35.7K and 18.8K of 54.5K).

**Revised estimate for Claude Sonnet 5.5**, from this profile: about $1.20 a case at 50 calls and $3 at the cap of 100, so $12 to $30 for ten cases, against $6 to $18 before. The answer turn now writes the whole history again, about a quarter of a case's cost. Claude Haiku 5.5 on the same profile: about $0.06 to $0.15 a case, $0.60 to $1.50 for ten. Both models keep the history whole: their 1M context is far above the largest case.

## Local runs: context length, speed, and the answer turn

The user ran `gpt-oss:20b` on single development cases at three context lengths.

| Context | Case | Turns | Seconds | Seconds a turn | Largest prompt | Result |
|---|---|---|---|---|---|---|
| 128K | case-036 (Hotel Reservation) | 46 | 945 | 20.5 | 19.5K | exact match: `geo`, `container_cpu_saturated` |
| 32K | case-073 (TrainTicket) | 26 | 360 | 13.8 | 19.1K | right service and edge, wrong kind (`application_exception`) |
| 64K | case-073 again | 18 | 237 | 13.2 | 14.9K | no answer: the answer turn called a tool |

- **Speed.** 64K is as fast a turn as 32K; 128K is about half as fast again, since more of the model sits on the CPU. A context large enough for the history doesn't change what the model sees, so local runs use 64K: as fast as 32K, with room for a case of 100 calls.
- **No answer.** The 64K run, like the 6-call smoke test before it, ended with a tool call at the answer turn. Its last thinking had the right service and edge; it wanted one more query to back the edge. The paper's harness scores this as an invalid answer. Claude's answer turn cannot do it (`tool_choice: none`), but Ollama has no `tool_choice`.
- **`--json-answer`**, off by default, holds a local model's answer turn to the official answer format as a JSON schema, with the 25 kinds as a fixed list and at least one piece of evidence per claim. Checked on one small request: the model then writes the answer in that format, where without it the same request invented the kind `high_cpu_usage`. With it, a local model can't lose a case to the format of its answer or to an invented kind. That makes the baseline a little stronger than the paper's, and so a harder bar for any design to beat. Each case's record says whether it was used.

## Result: the standard agent on Claude Haiku 5.5, ten development cases

Run by the user on 2026-11-12 with `--thinking-check error` and a $2 limit (`reports/openrca2-baseline-haiku`). It spent $0.26 by this project's price table, which assumes Haiku 5.5's cache reads cost a tenth of input; the console's bill is the real figure.

**Cost and time per case:** $0.015 to $0.037, mean $0.026, and 44 to 96 seconds. Each case used 18 to 42 tool calls in 12 to 23 turns, with 270K to 834K prompt tokens, nearly all cache reads. The largest single prompt was 82K tokens, under the 100K where Haiku's price rises. No thinking-block mismatch occurred, and every evidence query ran.

| Score | Mean |
|---|---|
| acc (exact match) | 0.70 |
| f1 | 0.70 |
| any-hit | 0.90 |
| all-hit | 0.90 |
| type-acc | 0.78 |
| node-F1 | 0.89 |
| edge-F1 | 0.81 |
| path-acc (needs a hit) | 0.67 |

- **Exact matches, 7 of 10.** They include the case with two required faults (case-352, both named), and case-237, where Haiku correctly left out a not-effective fault. It named no optional or not-effective fault in any case, so the draft rule for optional faults changed no score here.
- **The three misses.**
  - case-155 (OTel Demo): the wrong service. It named `product-catalog` as `application_method_slow`; the truth is `checkout` with `network_delay`.
  - case-216 and case-274: the right service with the wrong kind, the same confusion both times. A network partition to the database (`network_partition`) was read as `database_call_failed`. Seen from the calling service, a cut link to MySQL looks like failing database calls. Two cases are not a rule; this is something for phase 4 to study.
- **How far 7 of 10 can be trusted.** Its 95% interval runs from 40% to 89%. Under the public scorer, which counts every injected fault as required, the same answers score 60%: case-237's not-effective fault would count as a missed fault. Neither number can be set against the leaderboard's 46.40%, which is on the older 500-case data, with other cases and other labels.

**The local model, for comparison.** `gpt-oss:20b` took 4 to 16 minutes a case, against Haiku's 1 to 2. On the three sample cases it answered, it got one exact match (case-036), named the right service with the wrong kind once (case-073), and blamed the entry service once (case-095); Haiku got all three right. Two more cases stopped on Ollama errors. On this evidence a local model has no role in the baseline. Haiku is cheap enough that the whole development set would cost about $2.60 a run, and the 355 held-out cases about $9.
