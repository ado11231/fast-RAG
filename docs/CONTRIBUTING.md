# Contributing to fastrag

Thanks for considering a contribution. fastrag is intentionally focused —
read this before building so your work fits cleanly.

---

## The One Rule

fastrag does one thing: **data in, queryable knowledge out.**

If your contribution adds something outside that loop (agents, memory, LLM chaining,
conversation history, frontend UI), it belongs in a separate project, not here.
This isn't a rejection of the idea — it's how we stay useful to everyone.

If you're unsure whether something is in scope, open a Discussion before building.

---

## Best Ways to Contribute

**Plugins (highest impact)**
Build a loader, embedder, or store adapter for something you actually use.
Every plugin brings its community to fastrag. See [PLUGIN_GUIDE.md](docs/PLUGIN_GUIDE.md).

**Bug fixes**
Clear, reproducible bugs with a failing test attached get merged fast.

**Documentation**
Real examples from real use cases. If something confused you, fix it.

**Performance**
Chunking, embedding batching, store query speed — measured improvements welcome.

---

## What We Will Not Merge

- Features outside the data-in, knowledge-out scope
- Dependencies added to core without strong justification
- Breaking changes to the public API without a migration path
- Code without tests
- Plugins in the core package (plugins live in their own repos)

---

## Development Setup

```bash
git clone https://github.com/yourname/fastrag
cd fastrag
pip install -e ".[dev]"
```

Dev extras include pytest, ruff (linter), and mypy (type checker).

---

## Running Tests

```bash
pytest
```

All tests must pass before opening a PR.

---

## Code Standards

- Python 3.10+
- Type hints on every function signature
- Docstring on every public class and method
- `ruff check .` must pass with no errors
- `mypy fastrag/` must pass with no errors
- No print statements in library code — use `logging`
- File paths via `pathlib.Path`, never raw strings

---

## Opening a PR

1. Fork and create a branch named `feature/what-it-does` or `fix/what-it-fixes`
2. Write tests for your change
3. Make sure `pytest`, `ruff`, and `mypy` all pass
4. Write a clear PR description explaining what and why
5. Reference any related issues

Small focused PRs get reviewed and merged faster than large ones.

---

## Publishing a Community Plugin

Plugins live in their own repos and PyPI packages, not in this repo.
Once your plugin is published:

1. Open a PR that adds it to `PLUGINS.md`
2. Include: plugin name, PyPI package name, what it does, your GitHub handle

That's it — the community will find it.
