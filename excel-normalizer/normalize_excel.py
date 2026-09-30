#!/usr/bin/env python3
"""
normalize_excel.py — Bring numerical Excel workbooks onto a consistent scale.

What it does
------------
1. Ingests every Excel file in an input folder (or a single file).
2. Applies a normalisation method to every numeric column:
     - z-score  : (x - mean) / std          -> mean 0, std 1
     - minmax   : (x - min) / (max - min)   -> range [0, 1]
   By default statistics are computed PER FILE. With --global-stats the
   statistics are computed once over all files together, so the same value
   maps to the same normalised value in every workbook (recommended when the
   files are batches of the same dataset).
3. Writes the normalised data next to the originals (Excel or CSV).
4. Produces a before/after summary report (Excel with one sheet per file plus
   a "Summary" sheet) so the transformation can be verified.

Extension points (deliberately kept as separate functions so they can be
slotted into the pipeline later): `handle_missing_values`, `remove_duplicates`.

Usage
-----
    python normalize_excel.py --input ./data --output ./output --method zscore
    python normalize_excel.py --input ./data --method minmax --global-stats --format csv
    python normalize_excel.py --input file.xlsx --sheet Sheet1

Requirements: pandas, numpy, openpyxl  (pip install pandas numpy openpyxl)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

METHODS = ("zscore", "minmax")


# --------------------------------------------------------------------------- #
# Extension points (not active yet — the client said these are not priorities)
# --------------------------------------------------------------------------- #
def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Placeholder for a future missing-value strategy (drop, mean, median...).

    Currently returns the frame unchanged. Normalisation below is NaN-safe:
    pandas skips NaN when computing mean/std/min/max, and NaN stays NaN.
    """
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Placeholder for duplicate-row removal (e.g. df.drop_duplicates())."""
    return df


# --------------------------------------------------------------------------- #
# Core normalisation
# --------------------------------------------------------------------------- #
def compute_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Descriptive statistics for every numeric column of a frame."""
    num = df.select_dtypes(include=[np.number])
    stats = pd.DataFrame(
        {
            "count": num.count(),
            "mean": num.mean(),
            "std": num.std(ddof=0),
            "min": num.min(),
            "max": num.max(),
        }
    )
    stats.index.name = "column"
    return stats


def normalize(df: pd.DataFrame, method: str, stats: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of `df` with numeric columns normalised using `stats`.

    `stats` may come from this file (per-file mode) or from all files
    together (global mode). Non-numeric columns are left untouched.
    Columns with zero variance / zero range are set to 0 instead of NaN/inf.
    """
    out = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        x = df[col].astype(float)
        if method == "zscore":
            mean, std = stats.loc[col, "mean"], stats.loc[col, "std"]
            out[col] = (x - mean) / std if std > 0 else 0.0
        elif method == "minmax":
            lo, hi = stats.loc[col, "min"], stats.loc[col, "max"]
            rng = hi - lo
            out[col] = (x - lo) / rng if rng > 0 else 0.0
        else:  # pragma: no cover
            raise ValueError(f"Unknown method: {method}")
    return out


# --------------------------------------------------------------------------- #
# I/O helpers
# --------------------------------------------------------------------------- #
def list_input_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files = sorted(p for p in path.glob("*.xls*") if not p.name.startswith("~$"))
    if not files:
        sys.exit(f"No Excel files found in {path}")
    return files


def read_workbook(path: Path, sheet: str | int | None) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet if sheet is not None else 0)


def write_output(df: pd.DataFrame, out_path: Path, fmt: str) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "csv":
        target = out_path.with_suffix(".csv")
        df.to_csv(target, index=False)
    else:
        target = out_path.with_suffix(".xlsx")
        df.to_excel(target, index=False)
    return target


def build_report(before: dict[str, pd.DataFrame], after: dict[str, pd.DataFrame],
                 method: str, report_path: Path) -> None:
    """One sheet per file with before/after stats side by side + a summary."""
    summary_rows = []
    with pd.ExcelWriter(report_path, engine="openpyxl") as xw:
        for name in before:
            b, a = before[name], after[name]
            merged = b.join(a, lsuffix="_before", rsuffix="_after")
            merged.to_excel(xw, sheet_name=name[:31])  # Excel sheet-name limit
            # Verification per column
            for col in a.index:
                if method == "zscore":
                    ok = abs(a.loc[col, "mean"]) < 1e-9 and (abs(a.loc[col, "std"] - 1) < 1e-9 or a.loc[col, "std"] == 0)
                else:
                    ok = a.loc[col, "min"] >= -1e-9 and a.loc[col, "max"] <= 1 + 1e-9
                summary_rows.append({"file": name, "column": col, "method": method,
                                     "rows": int(b.loc[col, "count"]),
                                     "mean_after": round(float(a.loc[col, "mean"]), 6),
                                     "std_after": round(float(a.loc[col, "std"]), 6),
                                     "min_after": round(float(a.loc[col, "min"]), 6),
                                     "max_after": round(float(a.loc[col, "max"]), 6),
                                     "check": "OK" if ok else "REVIEW"})
        pd.DataFrame(summary_rows).to_excel(xw, sheet_name="Summary", index=False)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", "-i", required=True, help="Excel file or folder with Excel files")
    ap.add_argument("--output", "-o", default="output", help="Output folder (default: ./output)")
    ap.add_argument("--method", "-m", choices=METHODS, default="zscore", help="Normalisation method")
    ap.add_argument("--format", "-f", choices=("xlsx", "csv"), default="xlsx", help="Output format")
    ap.add_argument("--sheet", default=None, help="Sheet name or index to read (default: first sheet)")
    ap.add_argument("--global-stats", action="store_true",
                    help="Compute mean/std/min/max over ALL files together instead of per file")
    args = ap.parse_args(argv)

    in_path, out_dir = Path(args.input), Path(args.output)
    sheet = int(args.sheet) if (args.sheet is not None and str(args.sheet).isdigit()) else args.sheet
    files = list_input_files(in_path)

    # 1. Ingest
    frames: dict[str, pd.DataFrame] = {}
    for f in files:
        df = read_workbook(f, sheet)
        df = remove_duplicates(handle_missing_values(df))  # extension points (no-ops today)
        frames[f.stem] = df
        print(f"read  {f.name}: {df.shape[0]} rows x {df.shape[1]} cols")

    # 2. Statistics (per file or global)
    global_stats = compute_stats(pd.concat(frames.values(), ignore_index=True)) if args.global_stats else None

    # 3. Normalise + write
    before, after = {}, {}
    for name, df in frames.items():
        stats = global_stats if global_stats is not None else compute_stats(df)
        norm = normalize(df, args.method, stats)
        target = write_output(norm, out_dir / f"{name}_{args.method}", args.format)
        before[name], after[name] = compute_stats(df), compute_stats(norm)
        print(f"wrote {target}")

    # 4. Report
    report = out_dir / f"normalization_report_{args.method}.xlsx"
    build_report(before, after, args.method, report)
    print(f"report {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
