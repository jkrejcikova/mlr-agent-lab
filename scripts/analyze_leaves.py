"""Analyze leaves.csv: counts per type, height-vs-width scatter, anomalies.

Run from the repo root:

    uv run --with pandas --with matplotlib python scripts/analyze_leaves.py \
        [path/to/leaves.csv]

Dependencies are supplied by `uv run --with` rather than `uv add`, because this
is a one-off look at a local dataset, not a runtime dependency of the project.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: write the PNG, open no window

import matplotlib.pyplot as plt
import pandas as pd

DEFAULT_CSV = Path("data/leaves.csv")
OUT_PNG = Path("data/leaves_scatter.png")
HEIGHT, WIDTH, TYPE = "Leaf height", "Leaf width", "Tree type"


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df[TYPE] = df[TYPE].astype(str).str.strip()
    return df


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    if not path.exists():
        print(f"no such file: {path}")
        return 1
    df = load(path)

    section("1. HOW MANY LEAVES OF EACH TYPE")
    counts = df[TYPE].value_counts(dropna=False)
    for name, n in counts.items():
        bar = "#" * round(40 * n / counts.max())
        print(f"  {name:<10} {n:>4}  ({100 * n / len(df):5.1f}%)  {bar}")
    print(f"  {'TOTAL':<10} {len(df):>4}")

    section("2. PER-TYPE MEASUREMENT STATS")
    stats = (
        df.groupby(TYPE)[[HEIGHT, WIDTH]]
        .agg(["count", "mean", "std", "min", "max"])
        .round(2)
    )
    print(stats.to_string())

    section("3. SCATTER PLOT")
    fig, ax = plt.subplots(figsize=(9, 6))
    for name in sorted(df[TYPE].unique()):
        sub = df[df[TYPE] == name]
        ax.scatter(
            sub[WIDTH], sub[HEIGHT], s=18, alpha=0.6, label=f"{name} (n={len(sub)})"
        )
    ax.set_xlabel(WIDTH)
    ax.set_ylabel(HEIGHT)
    ax.set_title("Leaf height vs width by tree type")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=120)
    print(f"  wrote {OUT_PNG}")

    # Width-vs-height ratio: which axis is really longer, per type.
    ratio = (
        (df[HEIGHT] / df[WIDTH]).groupby(df[TYPE]).agg(["mean", "min", "max"]).round(2)
    )
    print("\n  height/width ratio (1.0 = square leaf):")
    print(ratio.to_string())

    section("4. ANYTHING UNUSUAL")
    findings: list[str] = []

    # 4a: impossible / implausible values
    bad = df[
        (df[HEIGHT] <= 0) | (df[WIDTH] <= 0) | (df[HEIGHT] > 100) | (df[WIDTH] > 100)
    ]
    if len(bad):
        findings.append(
            f"{len(bad)} rows with non-positive or implausible (>100) values:"
        )
        findings.append(bad.to_string())

    # 4b: NaNs, and whitespace/case variants hiding as new categories
    na = int(df[[HEIGHT, WIDTH, TYPE]].isna().sum().sum())
    if na:
        findings.append(f"{na} missing values")
    raw_types = pd.read_csv(path)[TYPE].astype(str)
    if raw_types.nunique() != df[TYPE].nunique():
        findings.append("type labels differ only by case/whitespace")

    # 4c: exact duplicate rows
    dup_mask = df.duplicated(keep=False)
    n_dup_groups = int(df.duplicated().sum())
    if n_dup_groups:
        findings.append(
            f"{n_dup_groups} duplicate rows ({int(dup_mask.sum())} rows involved, "
            f"{len(df) - n_dup_groups} unique):"
        )
        findings.append(
            df[df.duplicated(keep="first")]
            .sort_values([TYPE, HEIGHT])
            .head(20)
            .to_string()
        )

    # 4d: decimal precision as a fingerprint of mixed sources
    text_rows = path.read_text(encoding="utf-8").splitlines()[1:]

    def decs(row: str) -> int:
        parts = row.split(",")
        return max((len(p.split(".")[1]) if "." in p else 0) for p in parts[:2])

    precision = pd.Series([decs(r) for r in text_rows], name="decimals")
    counts_by_prec = precision.value_counts().sort_index()
    findings.append(
        f"decimal-precision mix in the 2 numeric columns:\n{counts_by_prec.to_string()}"
    )
    if len(counts_by_prec) > 1:
        findings.append(
            "  -> more than one precision regime usually means rows from different "
            "sources were concatenated (see the boundary check below)"
        )

    # 4e: does precision change partway down the file (concatenation point)?
    blocks = precision.ne(precision.shift()).cumsum()
    runs = precision.groupby(blocks).agg(["first", "size"])
    if len(runs) > 2:
        findings.append(
            f"{len(runs)} alternating precision runs; largest 5:\n"
            + runs.nlargest(5, "size").to_string()
        )

    # 4f: sentinel-ish repeated values
    top_h = df[HEIGHT].value_counts().head(5)
    findings.append(f"most frequent exact heights:\n{top_h.to_string()}")

    for f in findings:
        print("-" * 60)
        print(f)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
