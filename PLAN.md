# PLAN.md — progress and next step

Keep this current. Progress lives here, not in chat history. When you finish a
step, tick it and write the new next step before you stop.

## Where we are

Scaffolding is in place. Nothing has been implemented yet.

## Done

- [x] 2026-10-14 — Repo created and pushed public:
      `github.com/jkrejcikova/mlr-agent-lab`
- [x] 2026-10-14 — uv project initialised (`pyproject.toml`, `uv.lock`,
      Python `>=3.11`, resolved against CPython 3.14.7)
- [x] 2026-10-14 — Toolchain: `ruff` (lint + format) and `pytest` as dev deps
- [x] 2026-10-14 — `scripts/check.sh` runs all four checks, non-zero on failure
- [x] 2026-10-14 — Working rules written: `AGENTS.md`, loaded by `CLAUDE.md`
- [x] 2026-10-14 — Smoke test passes, checks green

## Not started

- [ ] Decide the first experiment (see next step)
- [ ] Pin down how runs are configured and recorded (seeds, config files,
      where results go) — `data/` and run artifacts are git-ignored by design
- [ ] Note: the environment records a non-Anthropic `ANTHROPIC_BASE_URL`
      (see `RUNS.md`); confirm which model is actually serving requests
      before reporting model identity in future run logs

## Next step

**Pick the first experiment and write it here as a concrete, checkable task.**

The repo can build, lint, and test, but it contains no science yet. The next
action is not code — it is deciding what this lab demonstrates, and writing
that down as a task with an observable success condition (something
`check.sh`-shaped, or a number to reproduce).

Suggested shape once chosen:

1. Write the goal and its success condition into this file.
2. One script under `src/`, one test under `tests/`.
3. Record the run in `RUNS.md`.

## Standing constraints

- No admin rights on this machine; tools install per-user to `~/.local/bin`.
- Python only via `uv`. No global `pip install`, ever.
- Repo is public: no secrets, no datasets, no course material.
