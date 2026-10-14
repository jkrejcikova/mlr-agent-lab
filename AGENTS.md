# AGENTS.md — working rules for this repository

Read this first, then `README.md`, then `PLAN.md`. These rules are binding for
any AI agent (Claude Code or otherwise) working here.

## 1. Read before you act

Before making any change, read:

1. `README.md` — what this project is and how to run it
2. `PLAN.md` — what is already done and what the current next step is

Do not start work that contradicts `PLAN.md` without saying so explicitly. If
you find the code disagreeing with either file, stop and report the mismatch
rather than quietly picking one.

## 2. Python: uv only

`uv` is the only supported way to touch Python here.

| Do | Do not |
| --- | --- |
| `uv run <cmd>` to execute anything | `python script.py` directly |
| `uv add <pkg>` for runtime deps | `pip install <pkg>` |
| `uv add --dev <pkg>` for tooling | `pip install --user <pkg>` |
| `uv sync` to reproduce the env | `python -m venv` + manual installs |
| `uv lock` after editing deps | editing `.venv` by hand |

**Never run a global `pip install`.** There is no supported global Python
environment on this machine; a bare `pip install` either fails or writes into
an interpreter shared with other projects, which produces "works on my
machine" breakage that is expensive to diagnose later.

`uv run` automatically creates `.venv` from `uv.lock` if it is missing, so a
fresh clone needs no separate setup step before the first command works.

Committed with the project: `pyproject.toml`, `uv.lock`. Never committed:
`.venv/` (see `.gitignore`).

## 3. Run checks before you say "done"

A change is not done when it is written; it is done when the checks pass.

```bash
bash scripts/check.sh
```

That runs `uv lock --check`, `ruff check`, `ruff format --check`, and `pytest`,
and exits non-zero if any of them fail.

Rules:

- Run it **after every change**, not once at the end of a session.
- Paste or summarise the real output. If it fails, say it failed and quote the
  error — do not describe the work as complete.
- If a check is genuinely not applicable, say which one and why. Do not delete
  or weaken a test to make the suite green; if a test is actually wrong, say so
  and explain the reasoning before changing it.
- Never claim a command succeeded without having run it in this session.
- Adding a check you had to write is fine; silently skipping one is not.

## 4. Keep the docs honest

- Update `PLAN.md` when you finish or change a step — progress lives there,
  not in chat.
- `README.md` describes the current reality, not intentions. If you change how
  something runs, change the README in the same commit.
- `RUNS.md` records what was attempted and how it was verified. Add an entry
  per significant piece of work.

## 5. Safety

- This repository is **public**. Never commit secrets, tokens, `.env` files,
  dataset files, or course material you do not have the right to publish.
  `.gitignore` covers the common cases; it is not a substitute for checking.
- Before any `git push`, review the staged file list
  (`git diff --cached --name-only`) and confirm nothing unexpected is in it.
- Never force-push, rewrite published history, or delete branches without an
  explicit request.
