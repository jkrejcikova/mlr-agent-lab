# SPEC.md — what this experiment has to achieve

This is the contract for the work. If a later decision contradicts this file,
either change the file first or say why in the commit message. Draft 1 was
written from the data analysis in `RUNS.md`, not from the lecture sheet, so
parts of it are my own reading and are marked **Open**.

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

**Open:** I do not know which of these two the assignment actually asks for.
If only the first is required, the second stays as a warning in the report
rather than a headline number.

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
- **Block C is inflated inside every class** — maple height 12.3 in A/B but
  15.4 in C, walnut width 6.4 in A/B but 8.8 in C (+34%). Because the shift
  happens within each species, it is not a species-mix effect. It is a
  different scale.
- **26 repeated rows** (46 rows involved). `7.5 x 3.8 cherry` appears four
  times, at CSV lines 304, 362, 429 and 473.
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

**Open:** whether the course allows scikit-learn or wants the models written by
hand.

**Test set.** Split **once, before any tuning**, stratified by class, seeded.
The test set is then untouched until the final numbers. Nothing is fitted on
it, no scaler, no encoder, nothing. Two test views, both fixed in advance:

- *Random split* — the standard number, comparable to a classmate's result.
- *Block split* — train only on blocks A+B (rows 1-302), test only on block C
  (rows 303-518). This is the number that shows whether the model learned the
  species or the session.

**Repeated rows.** A duplicated row must never sit in both train and test, or
the score is inflated by the model recognising the copy. Duplicates are grouped
by `(height, width, type)` before splitting.

**Open:** whether to drop the repeats or keep them as real re-measurements.

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
| `scripts/train_leaves.py` | split, tune, evaluate; fixed seed; takes a CSV path |
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
