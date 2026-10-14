# RUNS.md — what was asked, what was run, how it was checked

One entry per significant unit of work. Newest first. The point is that a
later reader (human or agent) can see **what was actually verified**, not just
what was intended. Write the check output, not a claim of success.

---

## 2026-10-14 — Repo scaffolding and working rules

### Model

Reported for this session: **not verifiable from inside the session.**

I could not open `/status` (it is an interactive UI command, not available to
me as a tool). What I could verify instead:

- This session's transcript records every turn under model id
  `qwen3.8-flash-next` (188 occurrences; no `claude-*` id appears anywhere).
- `~/.claude/settings.json` sets `ANTHROPIC_BASE_URL` to
  `https://llm.ai.e-infra.cz/`, a non-Anthropic proxy, with `ANTHROPIC_AUTH_TOKEN`
  present in the environment.
- Claude Code CLI version: `2.1.299`.

**Caveat, stated plainly:** these are not Claude model identifiers, and a
`model` field written by a proxy is a label, not proof of what served the
request. So I am not claiming this session was, or was not, served by a Claude
model — only that the local evidence does not support "Claude" as an answer.
**Confirm the authoritative value with `/status` and correct this entry.**
Anything in this file that depends on model identity is unreliable until you do.

### What was asked

Create `AGENTS.md` with working rules (read README/PLAN first; uv-only Python;
run checks before claiming done), have `CLAUDE.md` load it, and create
`README.md`, `PLAN.md`, `RUNS.md`.

### What was done

- `AGENTS.md` — rules, including a `scripts/check.sh` definition of "done".
- `CLAUDE.md` — loads `AGENTS.md`.
- `README.md` — goal and run instructions.
- `PLAN.md` — progress plus the current next step.
- `RUNS.md` — this file.
- Supporting work, because rule 3 is only meaningful if checks can run:
  `uv init` (`pyproject.toml`, `requires-python >=3.11`), `uv add --dev ruff
  pytest`, `scripts/check.sh`, `tests/test_smoke.py`.

Documenting "always use uv" in a repo with no `pyproject.toml` would have made
`uv run` fail for the next agent, so the uv project had to exist first.

### How it was checked

`bash scripts/check.sh` — full output recorded in the session:

```
=== uv lock --check ===   PASS
=== ruff check ===        PASS
=== ruff format --check === PASS
=== pytest ===            PASS   (1 passed)

ALL CHECKS PASSED
```

Also verified during setup, by running rather than asserting:

| Claim | How it was checked | Result |
| --- | --- | --- |
| `uv run` works with no venv | ran it on a fresh clone state | created `.venv`, printed `3.14.7` |
| `uv add` works | `uv add --dev pytest` | installed pytest 9.1.1 |
| Checks actually fail on bad input | (negative test, below) | exit code non-zero |

### Negative test — does the checker ever fail?

A green suite proves nothing unless it can go red. Added a deliberately broken
file and an unused import:

```
=== ruff check ===   F401 `os` imported but unused      FAIL
=== pytest ===       assert 1 == 2  → 1 failed, 1 passed FAIL
CHECKS FAILED                                            exit code 1
```

Both defects were caught and the script exited non-zero, so `check.sh` is a
real gate rather than a rubber stamp. Scratch files removed afterwards; `tests/`
contains only `test_smoke.py`.

### Also verified

| Claim | How | Result |
| --- | --- | --- |
| Fresh clone reaches green with no manual steps | cloned to a temp dir, `.venv` absent, ran `check.sh` | bootstrapped `.venv`, installed 7 packages, `ALL CHECKS PASSED`, exit 0 |
| `check.sh` works from any cwd | invoked by absolute path from `/tmp` | exit 0 (it `cd`s to the repo root itself) |
| `check.sh` keeps LF endings after commit | `.gitattributes` `*.sh eol=lf`; inspected bytes in the clone | shebang intact, `bash -n` clean |

`.gitattributes` was added because of this: git's `text=auto` default on
Windows would have committed CRLF for `check.sh`, and a CRLF shebang breaks the
script for the next person to clone.

### Not yet checked

- `check.sh` under PowerShell or cmd — it is bash. Use Git Bash.

### Follow-ups

1. Replace `tests/test_smoke.py` with real tests.
2. Get the real model id into the Model section above.
3. Add a `.ps1` wrapper for `check.sh` if PowerShell use is expected.
