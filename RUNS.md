# RUNS.md — what was asked, what was run, how it was checked

One entry per significant unit of work, **oldest first** — new entries are
appended at the end, which is the order a reader wants to follow to see how the
reasoning developed. (The first draft of this file said "newest first"; the
entries were never kept in that order, so the instruction was changed to match
what the file actually does.) The point is that a later reader (human or agent)
can see **what was actually verified**, not just what was intended. Write the
check output, not a claim of success.

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

## Step 1 — look at leaves.csv before modelling anything

**Entry written after the work**, on 2026-10-14, when I noticed this log jumped
from scaffolding straight to Step 3 and left out the two steps in between. The
numbers below are from re-running the script on 2026-10-14, not from memory.

### What was asked

Find out what is actually in `data/leaves.csv` before choosing a model, a
metric or a split.

### What was done

`scripts/analyze_leaves.py`: per-type counts, per-type height/width statistics,
a labelled scatter plot written headlessly to `data/leaves_scatter.png`, the
height/width ratio per type, and an anomalies section (duplicate rows, decimal
precision mix, precision-run boundaries, most frequent exact heights).

Dependencies come from `uv run --with pandas --with matplotlib` rather than
`uv add`, so a one-off look at a local file does not become a runtime
dependency of the project. The plot uses the `Agg` backend so no window opens.

### What it found

Four things that changed the plan; each is written up in `SPEC.md`:

| Finding | Evidence |
| --- | --- |
| Three precision blocks: rows 1-100 (1-2 dp), 101-302 (5-6 dp), 303-518 (1-2 dp) | precision histogram 283/33/76/126 by decimal count, plus the boundary check |
| Rows 303-518 are inflated **within every class** | per-class means recomputed by region, +14.5% to +38.9% |
| 20 repeated rows, 46 involved, 26 extra copies | `7.5 x 3.8 cherry` at CSV lines 304, 362, 429, 473 |
| One probable wrong label at CSV line 392 | `16.9 x 21.6` marked `cherry`; cherry's mean width is 5.33 |

The second row is the one that matters most: a random split can score well by
learning leaf size instead of species, and nothing in the score would show it.

### How it was checked

- Re-ran `uv run --with pandas --with matplotlib python scripts/analyze_leaves.py`
  on 2026-10-14: exit 0, counts 216/173/129 = 518, plot written.
- The region means were recomputed a second time with a separate pandas
  `groupby` on row position, independent of the analysis script. Both agree.
- The line-392 anomaly was confirmed by reading the row directly:
  `{'Leaf height': 16.9, 'Leaf width': 21.6, 'Tree type': 'cherry'}`.
- The four copies of `7.5,3.8,cherry` were confirmed by grepping the raw CSV
  rather than trusting the script's row indices.

### Worth recording as a mistake

The script's own output line reads
`26 duplicate rows (46 rows involved, 492 unique)`. In the interview that
followed I called the figure 492 an unverified guess that was wrong. It was
correct, and it had been printed by my own script since step 1. See step 3.

### Not yet checked

- No test covers this script; `check.sh` does not run it, because pandas is not
  a project dependency.
- The 100/302 block boundaries come from where the precision changes, which is
  an inference from the data, not a fact stated anywhere in the course material.

## Step 2 — SPEC.md, and the four decisions behind it

### What was asked

Write `SPEC.md` with the assignment's four sections — Goal, Context,
Constraints, "# Done when" — in plain B2 English, keeping the assignment's hint
questions as hints rather than answering them like a questionnaire. Before
finalising, ask about the decisions that were genuinely open.

### What was done

`SPEC.md` draft 1 (commit `4c3d291`), written from the step-1 findings rather
than from the lecture sheet, with every unresolved point marked **Open**
instead of filled in with a guess. Then four questions, and four answers:

| Question | Answer | Where it landed |
| --- | --- | --- |
| Which goal: accuracy, or honesty about the split? | **Both** | Goal section; the block-split number is a headline, not a footnote |
| The 26 repeated rows? | **Drop them** | Constraints; cost measured in step 3 |
| Is scikit-learn allowed? | **Yes** | Models section; version pinned via `uv.lock` |
| The 216 bigger-scale rows? | **Keep, and test on them** | Test set section; they are the honest test half |

Draft 2 (this commit) folds those in, marks each **Decided** with its date, and
moves what is still unresolved to an explicit list at the end: whether slides
are required, and what to do with the probable mislabel at line 392.

### How it was checked

- Every number carried into the spec was re-measured against the CSV, not
  copied from the draft. This caught a real error: the draft said walnut width
  went "6.4 to 8.8 (+34%)" between regions. Measured, it is 6.33 to 8.79,
  +38.9%. The spec now carries the full per-class table with all six numbers.
- The claim that region cannot be inferred from precision was tested rather
  than assumed. It is one-directional: all 202 rows with 3+ decimals are in
  rows 101-302, rows 1-100 have none, and rows 303-518 are entirely coarse. A
  coarse row therefore identifies nothing, which is what the argument needs.
- Each of the four answers was traced to a specific section, listed above.

### Worth recording as a mistake

In the interview reply I asserted that the "492 rows left" figure was an
unverified guess and was wrong. It was right. The reasoning that misled me: 46
rows are involved in a duplicate and 26 are extra copies, and I subtracted the
wrong one from 518 mentally. `518 - 26 = 492`. Step 3 measures all three
numbers so this cannot be argued about again.

### Not yet checked

- Whether the assignment really wants slides. The hint text mentions "results,
  report, slides"; the Done-when table does not list slides. The four interview
  questions covered other topics, so this was never put to you — it is recorded
  as open in `SPEC.md` rather than assumed either way.
- Whether `check.sh` should run `analyze_leaves.py`. It cannot, until pandas is
  a real dependency.

## Step 3 — what dropping duplicate rows really costs

- File `data\leaves.csv`: 518 rows.
- Distinct duplicated rows: **20**; rows involved: **46**.
- Extra copies removed (keep one per row): **26**. Rows left: **492** (95.0%).

The interview note said 492 rows left, and I replied calling that an
unverified guess. Measured, it is **492**, so the note was right and my
correction was the error. The arithmetic behind it, so nobody has to
re-derive it:

- 46 rows take part in a duplicate;
- 20 of those are distinct rows, so
- 46 - 20 = **26** copies are removed, and
- 518 - 26 = **492** rows remain.

The trap is that 'drop the 26 repeated rows' and 'drop the 46
rows involved in a repeat' are different instructions with different
answers. Only the first is what we want, and it is the one giving 492.

### How often a row repeats (over all distinct rows, so 1 means no repeat)

| Copies in file | Distinct rows |
| --- | --- |
| 1 | 472 |
| 2 | 15 |
| 3 | 4 |
| 4 | 1 |

### Effect on the classes

| Class | Before | Share | After | Share | Shift |
| --- | --- | --- | --- | --- | --- |
| maple | 216 | 41.7% | 208 | 42.3% | +0.6 pp |
| cherry | 173 | 33.4% | 162 | 32.9% | -0.5 pp |
| walnut | 129 | 24.9% | 122 | 24.8% | -0.1 pp |

The repeats fall in all three classes. The largest share change is
maple at +0.6 pp, so the class imbalance the model
has to handle is not changed by the cleanup.

### Precision and region are two different dimensions

| Region | fine (3+ dp) | coarse (1-2 dp) |
| --- | --- | --- |
| AB | 202 | 100 |
| C | 0 | 216 |

The relation is one-way. Every fine row is in AB
(0 fine rows in C), so a fine row does reveal its
region. But C is entirely coarse (216/
216), and so are
100 rows of AB. A coarse row therefore tells you
nothing about which region it came from, and those two sets of coarse
rows sit on different scales. That is where a random split goes wrong:
it can test only on coarse-AB rows while the real deployment rows are
coarse-C ones, and the accuracy number never shows the difference.

### Effect on the honest split (rows 1-302 vs the rest)

| Region | Before | After dedup |
| --- | --- | --- |
| AB | 302 | 296 |
| C | 216 | 196 |
| **Total** | 518 | 492 |

- Duplicated triples present on **both** sides of the split: **3**.
  Each is a leak risk under a random split, since one copy could train
  and an identical copy could be tested:
  - `16.5 x 17.0 maple` (AB x1, C x1)
  - `10.0 x 4.5 cherry` (AB x1, C x1)
  - `11.0 x 7.0 cherry` (AB x1, C x1)
- Test region keeps **196** rows after dedup, so the honest test
  still has enough data to mean something.

### Decision

From the interview: drop the duplicates. Measured cost is
26 rows and the test region keeps 196 rows, so the cost is
acceptable and the block split survives the cleanup.
