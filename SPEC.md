# SPEC.md — what this experiment has to achieve

This is the contract for the work. If a later decision contradicts this file,
either change the file first or say why in the commit message. Draft 1 was
written from the data analysis in `RUNS.md`, not from the lecture sheet, so
parts of it were my own reading and marked **Open**. Draft 2 closes four of
those, each marked **Decided** with the date and the reason; what is still open
is listed at the end.

# Goal

The short version: **can a model tell maple, walnut and cherry leaves apart
from only two numbers, and how much of its success is real?**

The interesting part of that question is the "how much is real". The file is
not one clean dataset. Rows 101-302 carry 5-6 decimals and rows 303-518 are
clearly measured on a bigger scale (see Context). A model can score well by
accident — by learning one leaf size instead of three species. So the result
has to answer two things:

1. How well can a simple classifier separate the three species from height and
   width?
2. Does that same model still work when it is tested on leaves from the block
   it was not trained on? This is the honest test of whether it learned the
   species or the measuring session.

**Decided (interview, 2026-10-14): both.** The honest view is not a footnote, it
is a headline number. A high random-split score that collapses on the block
split counts as a failed result, not a successful one.

# Context

**File.** `data/leaves.csv`, 10024 bytes. This is a local copy; the original is
`C:\Users\tomfr\Desktop\VUT\Machine_Learning\05\leaves.csv`. `data/` is
git-ignored, so the dataset is **not** in the public repo. The analysis script
takes a path argument, so a classmate points it at their own copy.

**Columns.** Three, all simple:

| Column | Type | Notes |
| --- | --- | --- |
| `Leaf height` | float | 1 dp, 2 dp, 5-6 dp (see Constraints) |
| `Leaf width` | float | same precision mix |
| `Tree type` | text | `maple`, `cherry`, `walnut` — clean, no case or space variants |

**Rows.** 519 lines in the file, 518 data rows, no missing values, no broken
lines.

| Class | Rows | Share | Height mean ± sd | Width mean ± sd |
| --- | --- | --- | --- | --- |
| maple | 216 | 41.7% | 13.48 ± 3.41 | 15.24 ± 4.05 |
| cherry | 173 | 33.4% | 9.33 ± 2.18 | 5.33 ± 1.92 |
| walnut | 129 | 24.9% | 15.32 ± 2.40 | 7.57 ± 2.13 |

The classes are unbalanced (1.7 : 1.3 : 1.0), which matters for the metric.

**Where it comes from.** The lecture folder `Machine_Learning/05`. Who made it
and how the measurements were taken I do not know.

**What step 1 found.** Four things that change the plan:

- **Three blocks, split by decimal precision.** Rows 1-100 (1-2 dp), rows
  101-302 (5-6 dp), rows 303-518 (1-2 dp again). Blocks A and B have almost
  identical per-class means, so they are the same population.
- **Block C is inflated inside every class.** Mean value in rows 1-302 versus
  rows 303-518, same species on both sides:

  | Class | Height AB → C | Width AB → C |
  | --- | --- | --- |
  | maple | 12.30 → 15.41 (+25.3%) | 13.87 → 17.49 (+26.1%) |
  | walnut | 14.18 → 16.44 (+16.0%) | 6.33 → 8.79 (+38.9%) |
  | cherry | 8.81 → 10.12 (+14.9%) | 5.04 → 5.77 (+14.5%) |

  Because the shift happens within each species, it is not a species-mix
  effect. It is a different scale.
- **20 rows are repeated, 46 rows take part in a repeat, 26 are extra copies.**
  `7.5 x 3.8 cherry` appears four times. `scripts/dedup_impact.py` prints all
  three numbers, because they are easy to confuse.
- **One probable wrong label:** line 392, `16.9 x 21.6` marked `cherry`. At
  21.6 wide it is four times cherry's mean width.

# Constraints

**Models.** Small and classical, because there are only two features — a deep
model would only hide the story. Baseline first, then:

| Model | Hyperparameters to search |
| --- | --- |
| Baseline: always guess maple | none (a floor, not a candidate) |
| Logistic regression | `C` log-scale 1e-3 to 1e3, on standardised inputs |
| k-nearest neighbours | `k` in 1,3,5,7,9,11; weights uniform vs distance |
| Decision tree | `max_depth` 1-8, `min_samples_leaf` 1-20 |
| Random forest | `n_estimators` 100, `max_depth` 3-12, `min_samples_leaf` 1-10 |

**Decided (interview): scikit-learn is allowed.** It is added with
`uv add scikit-learn` and the version is pinned in `uv.lock`, so the number a
classmate gets is the number I got.

**Test set.** Split **once, before any tuning**, stratified by class, seeded.
The test set is then untouched until the final numbers. Nothing is fitted on
it, no scaler, no encoder, nothing. Two test views, both fixed in advance:

- *Random split* — the standard number, comparable to a classmate's result.
- *Block split* — train only on blocks A+B (rows 1-302), test only on block C
  (rows 303-518). This is the number that shows whether the model learned the
  species or the session.

**Decided (interview): the 216 bigger-scale rows stay in the file and are used
as the test half.** They are not deleted as a nuisance, and they are not mixed
into training. They are the point: they are the only way to see whether the
model generalises outside the measuring session it was trained on. After
deduplication the two regions hold 296 training rows and 196 test rows, which
is enough for both numbers to mean something.

A coarse row does not reveal where it came from, so the shift is a hidden
factor and not a feature the model could simply read off the numbers. Measured:
all 202 rows with 3+ decimals are in rows 101-302, while rows 1-100 and rows
303-518 are entirely 1-2 decimal rows. Those two coarse groups overlap
completely in format and sit on different scales, and that is where a random
split goes wrong: it can test on coarse rows from rows 1-100 while the rows it
should represent are coarse rows from 303-518, and the score never shows it.

**Repeated rows.** Duplicates are keyed on `(height, width, type)`.

**Decided (interview): drop them, keeping one copy of each.** Measured in
`scripts/dedup_impact.py`: 20 rows are duplicated, 46 rows take part in a
duplicate, and keeping one copy removes 26 rows, leaving **492 of 518 (95.0%)**.
The repeats fall in all three classes, so the largest change in class share is
0.6 pp and the imbalance is untouched. Dropping them is cheap.

The reason to drop rather than merely group them is a leak that grouping alone
does not fix. Three duplicated triples sit on **both** sides of the block
boundary — `16.5 x 17.0 maple`, `10.0 x 4.5 cherry`, `11.0 x 7.0 cherry`, one
copy in each region. Deduplication removes those copies outright. The train
script still asserts that no key appears twice across the split, so this stays
checked rather than merely hoped for.

**Metric.** Macro-averaged F1, because the classes are unbalanced and plain
accuracy flatters the majority class. Balanced accuracy reported next to it.
The metric is computed on the **validation folds during tuning** and on the
**held-out test set only at the very end** — never to pick hyperparameters.

**Tuning.** Randomised search with cross-validation **on the training part
only**, 5 stratified folds, fixed `random_state`. Budget: at most 40
configurations per model, same budget for every model so the comparison is
fair. The winner is chosen by mean validation F1, and its test score is
reported once.

# Done when

A classmate can clone the repo, run one command, and get the same numbers
without asking me anything. Concretely, these must exist:

| File | Must contain |
| --- | --- |
| `data/leaves.csv` | the dataset, git-ignored (shared by other means) |
| `scripts/analyze_leaves.py` | the step-1 analysis, still runs |
| `scripts/dedup_impact.py` | the duplicate counts above, reproducible |
| `scripts/train_leaves.py` | dedup, split, tune, evaluate; fixed seed; takes a CSV path |
| `results/metrics.json` | every number below, machine-readable |
| `results/confusion_matrix.png` | final test confusion matrix, labelled |
| `results/leaves_scatter.png` | the data plot |
| `REPORT.md` | the numbers plus what they mean, in plain words |

Numbers that must be present, and that a classmate can check:

- row and class counts, so the split can be verified;
- the baseline (always maple) score — this is the floor to beat;
- best hyperparameters per model, by name and value;
- per-class precision, recall, F1, plus macro F1, on both test views;
- the random-split minus block-split gap, with one sentence saying why it is
  that size;
- the seed, the scikit-learn version, and the exact command line.

Checks that must pass before I call it done:

- `bash scripts/check.sh` exits 0;
- running the training script twice gives byte-identical `metrics.json`;
- no test row appears in training (assert this in code, do not assume it);
- the report's headline numbers match `results/metrics.json`;
- nothing from `data/` is committed to the public repo.

**Still open, not decided in the interview:**

- Whether slides are wanted. The assignment hints at "results, report, slides";
  the table above has no slides in it. If they are required, they are a
  separate deliverable and this file needs a row for them.
- What to do with the one probable wrong label at CSV line 392 (`16.9 x 21.6`
  marked `cherry`). It stays in the data for now, because removing a row on my
  own judgement is a bigger change than the single row is worth; it gets
  mentioned in the report instead.
