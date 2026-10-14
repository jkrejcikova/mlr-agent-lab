# mlr-agent-lab

Learning-agent experiments: small, reproducible Python experiments where an
agent learns to do something, with the runs and results kept next to the code.

> Status: scaffolding only. Nothing is implemented yet — see
> [PLAN.md](PLAN.md) for the current next step.

Start with [AGENTS.md](AGENTS.md) if you are an AI agent; it holds the working
rules.

## Requirements

- [uv](https://docs.astral.sh/uv/) — manages the interpreter, the virtualenv,
  and dependencies. Nothing else Python-related needs to be installed.
- Git.

There is no supported global Python environment here, and `pip` is not used
directly.

## Setup

```bash
git clone https://github.com/jkrejcikova/mlr-agent-lab
cd mlr-agent-lab
uv sync            # optional; `uv run` does this implicitly
```

`uv` creates `.venv/` from `uv.lock` on first use. `.venv/` is git-ignored.

## How to run things

| Task | Command |
| --- | --- |
| Run a script | `uv run python <script.py>` |
| Run a module | `uv run python -m <module>` |
| Add a runtime dependency | `uv add <package>` |
| Add a dev/test dependency | `uv add --dev <package>` |
| Reproduce the pinned env | `uv sync` |
| Run tests | `uv run pytest` |
| Lint | `uv run ruff check .` |
| Format check | `uv run ruff format --check .` |
| **Run every check** | `bash scripts/check.sh` |

`scripts/check.sh` is the single answer to "does this work?". Run it after
every change, not once at the end.

Run everything from the repo root. `check.sh` is a bash script — use Git Bash
on Windows (it ships with Git for Windows); a PowerShell wrapper does not
exist yet.

## Layout

```
AGENTS.md         working rules for AI agents — read first
CLAUDE.md         loads AGENTS.md into Claude Code
PLAN.md           progress and the current next step
RUNS.md           what was run, and how it was verified
README.md         this file
pyproject.toml    metadata and dependencies
uv.lock           pinned dependency versions (committed on purpose)
scripts/check.sh  runs every check; non-zero exit on failure
tests/            tests
.venv/            local only, git-ignored
```

`src/` does not exist yet — it gets created with the first experiment.

## Notes

- **This repo is public.** Do not commit secrets, `.env` files, datasets, or
  course material. `.gitignore` blocks the common cases — verify, then commit.
- Python `>=3.11` is supported; the local dev interpreter is CPython 3.14.7,
  which uv installs and manages itself.
- `uv`, `gh`, and similar tools live in `~/.local/bin` on the dev machine
  (user-scope install, no administrator rights).
