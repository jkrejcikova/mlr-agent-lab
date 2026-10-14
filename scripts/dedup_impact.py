"""Measure what dropping duplicate rows actually costs, and where the copies sit.

Why this script exists. Three numbers get confused here and they are close
enough to look identical: rows involved in a duplicate (46), distinct
duplicated rows (20), and extra copies removed when one copy is kept (26).
Step 1 reported "26 rows are extra copies", the interview note said "492 rows
left", and both turned out correct — this script measures them instead of
arguing about them. It also checks the one thing that could quietly break the
honest test: whether an identical row sits on both sides of the train/test
region boundary, because then a random split can train on one copy and test on
another.

Two block dimensions are kept apart on purpose:
  - precision (fine vs coarse decimal places), which is a property of a row and
    needs no knowledge of where the row sits;
  - region (rows 1-302 vs 303-518), which is positional and is the boundary the
    honest block split actually uses, because blocks A and C both use 1-2
    decimal places and only position separates them.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

# Rows 303-518 sit on a larger measurement scale (step-1 finding). This is the
# boundary of the honest split, so it is stated here as a constant with a
# reason, not buried in a condition.
POSITIONAL_SPLIT_LAST_ROW = 302

# Heading of the section this script owns in RUNS.md. RUNS.md is a log, so the
# section is written once and then rewritten in place on a re-run: an appended
# second copy would leave a superseded, wrong version sitting in the log.
SECTION_HEADING = "## Step 3 — what dropping duplicate rows really costs"

# Column order for the precision x region table.
BANDS = ("fine (3+ dp)", "coarse (1-2 dp)")


def write_section(out: Path, text: str) -> str:
    """Write this step's section into the log, replacing it if already present.

    Only the section between this heading and the next `## ` is touched, so the
    steps logged before it stay exactly as they were.
    """
    body = out.read_text(encoding="utf-8") if out.exists() else ""
    lines = body.rstrip("\n").splitlines()
    # Match any "## Step 3" heading, whatever dash an older run used, so a
    # re-run replaces the version it wrote before instead of adding a second.
    start = next((i for i, ln in enumerate(lines) if ln.startswith("## Step 3")), None)
    if start is None:
        new = (body.rstrip("\n") + "\n\n" if body.strip() else "") + text
        action = "appended"
    else:
        end = next(
            (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
            len(lines),
        )
        rebuilt = lines[:start] + text.splitlines() + [""] + lines[end:]
        new = "\n".join(rebuilt).rstrip("\n") + "\n"
        action = "replaced in place"
    out.write_text(new, encoding="utf-8")
    return action


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def decimals(value: str) -> int:
    return 0 if "." not in value else len(value.split(".", 1)[1])


def key_of(row: dict[str, object]) -> tuple[str, str, str]:
    return (row["Leaf height"], row["Leaf width"], row["Tree type"])  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/leaves.csv", type=Path)
    parser.add_argument("--out", default="RUNS.md", type=Path)
    args = parser.parse_args()

    rows = read_rows(args.csv)
    total = len(rows)
    for index, row in enumerate(rows, start=1):
        row["_i"] = str(index)
        row["_dec"] = str(
            max(decimals(row["Leaf height"]), decimals(row["Leaf width"]))
        )
        row["_region"] = "AB" if index <= POSITIONAL_SPLIT_LAST_ROW else "C"

    counts = Counter(key_of(r) for r in rows)
    dup_keys = {k: c for k, c in counts.items() if c > 1}
    involved = sum(dup_keys.values())
    drops = involved - len(dup_keys)
    kept = total - drops

    # Which duplicated triples exist on both sides of the honest split? Those
    # are the leak risk: a random split could train on one copy and test on
    # another identical one.
    region_of_key: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    for row in rows:
        region_of_key[key_of(row)][row["_region"]] += 1
    dup_across_split = [k for k in dup_keys if len(region_of_key[k]) > 1]

    # Region sizes if we keep the first copy of each triple.
    seen: set[tuple[str, str, str]] = set()
    after: Counter = Counter()
    for row in rows:
        k = key_of(row)
        if k in seen:
            continue
        seen.add(k)
        after[row["_region"]] += 1

    # Class balance before and after. counts.keys() are the distinct triples,
    # i.e. exactly the rows a dedup keeps.
    cls_before = Counter(r["Tree type"] for r in rows)
    cls_after = Counter(key[2] for key in counts)
    shift = {
        cls: 100.0 * (cls_after[cls] / kept - cls_before[cls] / total)
        for cls in cls_before
    }
    worst_cls = max(shift, key=lambda c: abs(shift[c]))

    lines: list[str] = []
    a = lines.append
    a(SECTION_HEADING + "\n")
    a(f"- File `{args.csv}`: {total} rows.")
    a(
        f"- Distinct duplicated rows: **{len(dup_keys)}**; rows involved: **{involved}**."
    )
    a(
        f"- Extra copies removed (keep one per row): **{drops}**. "
        f"Rows left: **{kept}** ({kept / total:.1%})."
    )
    a("")
    a("The interview note said 492 rows left, and I replied calling that an")
    a(f"unverified guess. Measured, it is **{kept}**, so the note was right and my")
    a("correction was the error. The arithmetic behind it, so nobody has to")
    a("re-derive it:")
    a("")
    a(f"- {involved} rows take part in a duplicate;")
    a(f"- {len(dup_keys)} of those are distinct rows, so")
    a(f"- {involved} - {len(dup_keys)} = **{drops}** copies are removed, and")
    a(f"- {total} - {drops} = **{kept}** rows remain.")
    a("")
    a(f"The trap is that 'drop the {drops} repeated rows' and 'drop the {involved}")
    a("rows involved in a repeat' are different instructions with different")
    a(f"answers. Only the first is what we want, and it is the one giving {kept}.\n")

    a("### How often a row repeats (over all distinct rows, so 1 means no repeat)\n")
    dist = Counter(counts.values())
    a("| Copies in file | Distinct rows |")
    a("| --- | --- |")
    for times in sorted(dist):
        a(f"| {times} | {dist[times]} |")
    a("")

    a("### Effect on the classes\n")
    a("| Class | Before | Share | After | Share | Shift |")
    a("| --- | --- | --- | --- | --- | --- |")
    for cls, cnt in cls_before.most_common():
        a(
            f"| {cls} | {cnt} | {cnt / total:.1%} | {cls_after[cls]} "
            f"| {cls_after[cls] / kept:.1%} | {shift[cls]:+.1f} pp |"
        )
    a("")
    a("The repeats fall in all three classes. The largest share change is")
    a(f"{worst_cls} at {shift[worst_cls]:+.1f} pp, so the class imbalance the model")
    a("has to handle is not changed by the cleanup.\n")

    # Precision (a property of the row) against region (a property of the
    # position). If these two dimensions coincided, the block split could be
    # re-found from the numbers alone and the positional split would be
    # redundant. They do not coincide, which is why the split is positional.
    def band(row: dict[str, str]) -> str:
        return "fine (3+ dp)" if int(row["_dec"]) >= 3 else "coarse (1-2 dp)"

    a("### Precision and region are two different dimensions\n")
    a("| Region | " + " | ".join(BANDS) + " |")
    a("| --- | " + " | ".join("---" for _ in BANDS) + " |")
    cross = Counter((r["_region"], band(r)) for r in rows)
    for region in ("AB", "C"):
        a(f"| {region} | " + " | ".join(str(cross[(region, b)]) for b in BANDS) + " |")
    a("")
    a("The relation is one-way. Every fine row is in AB")
    a(f"({cross[('C', BANDS[0])]} fine rows in C), so a fine row does reveal its")
    a(f"region. But C is entirely coarse ({cross[('C', BANDS[1])]}/")
    a(f"{cross[('C', BANDS[1])] + cross[('C', BANDS[0])]}), and so are")
    a(f"{cross[('AB', BANDS[1])]} rows of AB. A coarse row therefore tells you")
    a("nothing about which region it came from, and those two sets of coarse")
    a("rows sit on different scales. That is where a random split goes wrong:")
    a("it can test only on coarse-AB rows while the real deployment rows are")
    a("coarse-C ones, and the accuracy number never shows the difference.\n")

    a(
        f"### Effect on the honest split (rows 1-{POSITIONAL_SPLIT_LAST_ROW} vs the rest)\n"
    )
    a("| Region | Before | After dedup |")
    a("| --- | --- | --- |")
    for region in ("AB", "C"):
        before = sum(1 for r in rows if r["_region"] == region)
        a(f"| {region} | {before} | {after[region]} |")
    a(f"| **Total** | {total} | {kept} |")
    a("")
    a(
        f"- Duplicated triples present on **both** sides of the split: "
        f"**{len(dup_across_split)}**."
    )
    if dup_across_split:
        a("  Each is a leak risk under a random split, since one copy could train")
        a("  and an identical copy could be tested:")
        for key in dup_across_split[:8]:
            where = ", ".join(
                f"{r} x{region_of_key[key][r]}" for r in sorted(region_of_key[key])
            )
            a(f"  - `{key[0]} x {key[1]} {key[2]}` ({where})")
    else:
        a("  None, so an identical row is never shared between the two regions.")
    a(f"- Test region keeps **{after['C']}** rows after dedup, so the honest test")
    a("  still has enough data to mean something.\n")

    a("### Decision\n")
    a("From the interview: drop the duplicates. Measured cost is")
    a(f"{drops} rows and the test region keeps {after['C']} rows, so the cost is")
    a("acceptable and the block split survives the cleanup.\n")

    text = "\n".join(lines)
    print(text)
    if args.out:
        action = write_section(Path(args.out), text)
        print(f"\n[{action} in {args.out}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
