# Excel Numerical Data Normalization

Command-line tool that brings numerical Excel workbooks onto a consistent scale
(z-score or min-max), writes the normalised data back to Excel/CSV and produces a
before/after statistics report to verify the transformation.

## Quick start

```bash
pip install -r requirements.txt

# z-score, per-file statistics, Excel output
python normalize_excel.py --input sample_data --output output --method zscore

# min-max in [0,1], statistics computed over all files together, CSV output
python normalize_excel.py --input sample_data --output output --method minmax --global-stats --format csv
```

Run it on the included `sample_data/` folder (3 workbooks, 200 rows x 5 numeric columns each)
to reproduce the files in `sample_output/`.

## Options

| Option | Meaning |
|---|---|
| `--input, -i` | One Excel file or a folder containing `.xlsx`/`.xls` files (required) |
| `--output, -o` | Output folder (default `./output`) |
| `--method, -m` | `zscore` (mean 0, std 1) or `minmax` (range 0-1). Default `zscore` |
| `--format, -f` | `xlsx` (default) or `csv` |
| `--sheet` | Sheet name or index to read (default: first sheet) |
| `--global-stats` | Compute mean/std/min/max over **all** files together instead of per file |

## Which method, and per-file or global?

* **z-score** is the safer default: it keeps the shape of the distribution, is not
  distorted by a single extreme value as much as min-max, and is what most
  statistical and machine-learning methods expect.
* **min-max** is better when you need a bounded 0-1 range (dashboards, neural
  networks with bounded inputs, weighted scores).
* If the workbooks are batches of the **same** dataset, use `--global-stats`:
  otherwise the value `70` would map to a different normalised value in each
  file and the files would not be comparable.

## Output

* `<file>_<method>.xlsx|csv` — normalised copy of each workbook (non-numeric columns untouched).
* `normalization_report_<method>.xlsx` — one sheet per file with before/after
  count, mean, std, min, max side by side, plus a `Summary` sheet with a
  per-column `OK` / `REVIEW` check (mean≈0 & std≈1 for z-score, range within
  [0,1] for min-max).

## Extending

`handle_missing_values()` and `remove_duplicates()` are already wired into the
pipeline as no-op functions, so a missing-value strategy or duplicate removal can
be added later without touching the rest of the code. Columns with zero variance
or zero range are set to 0 instead of producing NaN/inf.

## Requirements

Python 3.9+, pandas, numpy, openpyxl. Tested with pandas 3.0, numpy 2.4.
