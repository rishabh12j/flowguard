# Contributing to FlowGuard

Thanks for your interest. FlowGuard works end to end on synthetic incidents. What it needs most is a way to read evidence from real systems, so **connectors are the most valuable contribution**. Start with [docs/connectors.md](docs/connectors.md): it has the contract a connector must meet and the list of connectors wanted.

Bug reports, clearer docs, new test incidents, and evaluation improvements are welcome too.

## Set up

You need Python 3.11 or later. Ollama is only needed for the tests marked `llm` and for evaluations.

```bash
pip install -e ".[dev]"
pytest                      # no model needed
```

To run FlowGuard itself, follow the [Quick start](README.md#quick-start).

## Before you open a pull request

Run the same checks as CI:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Then:

- Keep each pull request to one change, and explain what it changes, why, and how you tested it.
- Add a line to [`CHANGELOG.md`](CHANGELOG.md).
- For a larger change, such as a new dependency or a change to the graph, the tools, or the audit record, open an issue first to agree on the design.

## Ground rules

FlowGuard is built so that a model can't cause harm even when it's wrong or manipulated. Contributions must keep that true.

1. **Tools stay read-only.** MCP tools read evidence; they never change a system. An action that changes something is only ever recommended, and needs a person's approval.
2. **Code decides, not the model.** Confidence, risk, which actions are allowed, and whether approval is needed are set by code and the action catalogue. A prompt change must never become the only thing enforcing a rule.
3. **Every rule has a test that fails without it.** [`tests/unit/test_safety.py`](tests/unit/test_safety.py) uses a model that obeys injected instructions, to show the controls hold anyway. Extend it when you add a control.
4. **No secrets or real data.** Never commit credentials, tokens, or real customer or company data, including in test fixtures and incidents. Settings come from environment variables; [`.env.example`](.env.example) lists them, commented out.
5. **Honest evaluation.** Incidents marked `held_out`, and the benchmark's `test` families, are run once to measure FlowGuard and never used to tune it. Tune on the tuning incidents or the benchmark's `dev` families. When you report a number, say which set it came from. [docs/evaluation.md](docs/evaluation.md) explains why.

## Reporting a security problem

Please don't open a public issue. Use the repository's **Security** tab and choose "Report a vulnerability", so it can be fixed before it's disclosed.

## Licence

FlowGuard is licensed under the [Apache License 2.0](LICENSE). By contributing, you agree that your contribution is licensed under the same terms.
