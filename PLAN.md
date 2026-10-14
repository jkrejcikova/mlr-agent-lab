# PLAN.md — progress and next step

Keep this current. Progress lives here, not in chat history. When you finish a
step, tick it and write the new next step before you stop.

## Where we are

The data has been analysed, `SPEC.md` is written, and the four key decisions
were put to the user and answered. No model has been trained yet — the whole
training step is what remains.

## Done

- [x] 2026-10-14 — Repo created and pushed public:
      `github.com/jkrejcikova/mlr-agent-lab`
- [x] 2026-10-14 — uv project initialised (`pyproject.toml`, `uv.lock`,
      Python `>=3.11`, resolved against CPython 3.14.7)
- [x] 2026-10-14 — Toolchain: `ruff` (lint + format) and `pytest` as dev deps
- [x] 2026-10-14 — `scripts/check.sh` runs all four checks, non-zero on failure
- [x] 2026-10-14 — Working rules written: `AGENTS.md`, loaded by `CLAUDE.md`
- [x] 2026-10-14 — Smoke test passes, checks green
- [x] 2026-10-14 — Dataset chosen: `data/leaves.csv` (518 rows, 2 numeric
      features, 3 tree species), git-ignored, shared outside the repo
- [x] 2026-10-14 — Step 1: `scripts/analyze_leaves.py` — counts, per-type
      stats, scatter, anomalies. Found three precision blocks, a within-class
      scale shift in rows 303-518, 26 duplicate copies, one probable mislabel
- [x] 2026-10-14 — `SPEC.md` draft 1 written from the analysis, unknowns marked
      Open rather than guessed
- [x] 2026-10-14 — Four key decisions put to the user: goal is accuracy **and**
      honesty about the split; duplicates dropped; scikit-learn allowed; the
      bigger-scale rows kept and used as the honest test
- [x] 2026-10-14 — Step 3: `scripts/dedup_impact.py` — measured the cost of
      dropping duplicates (26 rows, 492 left, 196 test rows) and found 3
      duplicated triples straddling the train/test boundary
- [x] 2026-10-14 — `SPEC.md` draft 2: the four answers folded in, each marked
      Decided; every carried-over number re-measured (one was wrong and is
      corrected); remaining unknowns listed explicitly

## Not started

- [ ] Add scikit-learn (`uv add scikit-learn`) — not yet a dependency
- [ ] `scripts/train_leaves.py`: dedup, both splits, tuned models, both metrics
- [ ] `results/metrics.json` and the two PNGs
- [ ] `REPORT.md`
- [ ] Decide whether slides are required (see `SPEC.md`, still open)
- [ ] Note: the environment records a non-Anthropic `ANTHROPIC_BASE_URL`
      (see `RUNS.md`); confirm which model is actually serving requests
      before reporting model identity in future run logs

## Next step

**Implement `scripts/train_leaves.py` and produce the artifacts `SPEC.md`
lists under "# Done when".**

The experiment is decided and the spec is signed off, so this step is code.
Success condition, taken from `SPEC.md` and checkable without asking me:

1. `uv add scikit-learn` succeeds and `uv lock --check` stays green.
2. `uv run python scripts/train_leaves.py --csv data/leaves.csv` exits 0 and
   writes `results/metrics.json`, `results/confusion_matrix.png`.
3. Running it twice gives **byte-identical** `results/metrics.json`.
4. The script asserts in code that no test row and no duplicate key appears in
   training, and that assertion is exercised by a real test under `tests/`.
5. `metrics.json` contains, for each of the four models and both test views:
   best hyperparameters, per-class precision/recall/F1, macro F1, balanced
   accuracy — plus the baseline score, the seed, and the scikit-learn version.

Then `REPORT.md`, whose headline numbers must be copied from `metrics.json`
rather than typed from memory.

## Standing constraints

- No admin rights on this machine; tools install per-user to `~/.local/bin`.
- Python only via `uv`. No global `pip install`, ever.
- Repo is public: no secrets, no datasets, no course material.
