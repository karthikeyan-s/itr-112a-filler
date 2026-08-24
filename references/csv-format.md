# 112A CSV format — the 14 columns

The header **text and column order** are fixed by the Income-Tax Department — copy the column wording
from the user's blank template (do not retype it — subtle wording/spacing differences cause rejection).
But don't copy the template's **formatting** (quoting style, trailing commas) assuming it's correct — see
"Quoting style and line endings" below for why that assumption failed twice. The columns, in order:

| # | Short name | Meaning |
|---|---|---|
| 1 | 1a (BE/AE) | `BE` if acquired on/before 31-Jan-2018, else `AE` |
| 2 | ISIN | Real ISIN for BE rows; literal `INNOTREQUIRD` for AE rows |
| 3 | Name | Security name, **alphanumeric + spaces only**; literal `CONSOLIDATED` for AE rows |
| 4 | Units | Quantity sold (this lot). **Blank for AE rows.** |
| 5 | Sale price / unit | **Blank for AE rows.** |
| 6 | Total FVC | Full value of consideration. BE: `round(units × price)`. AE: total AE sale, entered directly. |
| 7 | Cost of acquisition w/o indexation | `max(col8, col9)` |
| 8 | Cost of acquisition | Actual purchase cost |
| 9 | (if BE) lower of col6 & col11 | `min(col6, col11)` for BE; `0` for AE |
| 10 | FMV per unit 31-Jan-2018 | **Blank for AE rows.** |
| 11 | Total FMV 31-Jan-2018 | BE: `round(units × col10)`. `0` for AE. |
| 12 | Expenditure | Transfer expenses (usually 0 if sale value already net of brokerage) |
| 13 | Deductions | `col7 + col12` |
| 14 | Balance (taxable LTCG) | `col6 − col13`. May be negative (a long-term loss) — that's valid. |

## BE row (grandfathering applies)

Grandfathering gives the taxpayer the **higher** of actual cost and the **lower** of (sale value, 31-Jan-2018
FMV). Concretely, per lot:

```
col6  = round(units × sale_price)
col11 = round(units × fmv_31jan2018)
col9  = min(col6, col11)
col7  = max(col8, col9)          # col8 = actual cost
col13 = col7 + col12             # col12 usually 0
col14 = col6 − col13
```

**Worked example (BE):** 100 shares, sale ₹248.85, actual cost ₹63/sh (₹6,300), FMV 31-Jan-2018 ₹126.55.
- col6 = round(100×248.85) = 24,885
- col11 = round(100×126.55) = 12,655
- col9 = min(24,885, 12,655) = 12,655
- col7 = max(6,300, 12,655) = 12,655
- col14 = 24,885 − 12,655 = **12,230**

Note the FMV floor (12,655) beat the real cost, so the exact cost didn't matter — this is why a missing
cost on an appreciated pre-2018 holding is tax-neutral (enter col8 = 0).

## AE row (no grandfathering) — one consolidated row per source

```
1a = AE
ISIN = INNOTREQUIRD
Name = CONSOLIDATED
col4, col5, col10 = blank
col6  = Σ (sale consideration of all AE lots for this source)
col8  = col7 = Σ (cost of all AE lots for this source)
col9  = 0
col11 = 0
col12 = 0
col13 = col7
col14 = col6 − col13
```

**When bought-value is missing but Gain/Loss is given:** some broker statements show the bought/cost
column as 0 yet still print a correct Gain/Loss (computed internally against the real cost). In that case:

```
col6  = Σ sale
col14 = Σ Gain/Loss        (authoritative from the broker)
col8  = col7 = col6 − col14 (derive cost from sale and gain)
```

## Rounding

- Money columns (6,7,8,9,11,12,13,14): **whole rupees** (Python `round()`).
- Units (4): keep decimals as in the statement.
- Prices (5,10): keep decimals.
- The sum of col14 across all rows is the grand-total taxable LTCG. The ITR utility recomputes col6/col14
  from the raw columns with its own rounding, so expect it to differ from your sum by a few rupees. That
  is normal and not an error.

## Name sanitisation

Strip the Name (col3) to letters, digits, and spaces. Remove `, . / - _ ( ) & @ ' " ; :` and similar.
Example: `CITY UNION BANK LIMITED EQ NEW RS. 1/-` → `CITY UNION BANK LIMITED EQ NEW RS 1`. AE rows always
use `CONSOLIDATED`.

## Quoting style and line endings — use QUOTE_MINIMAL, not QUOTE_ALL

**Root cause of two rounds of upload rejections, now confirmed:** some 112A templates the Department
hands out (or that pass through an intermediate export/re-save) come pre-formatted with **every field
wrapped in quotes** (`"BE","INE208A01029","ASHOKLEY",...`) and sometimes a dangling trailing comma on the
header line. Matching that formatting exactly still gets rejected by the ITR utility — first as "extra
column" (from the trailing comma), then as **"Please enter valid input" on almost every column** once the
comma was fixed. The real problem was the quoting itself: the utility's parser doesn't reliably recognise
a quoted numeric token (`"248.85"`) as a valid number, so wrapping every field in quotes — even after
fixing the column count — still fails validation across the board.

**The confirmed-working format** (verified against a template + filled CSV that the user successfully
uploaded) is standard CSV **QUOTE_MINIMAL**: plain unquoted values everywhere, with quotes appearing
*only* on the few header cells whose description text itself contains a literal comma (e.g. "...on or
before 31st January, 2018..."). Data rows are entirely unquoted, including text fields like `ASHOKLEY` or
`CONSOLIDATED`. Line endings are CRLF (`\r\n`) after every line, **including a trailing CRLF after the
final data row.**

**Always generate the output this way:**

```python
import csv
with open(output_path, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
    w.writerow(header)      # 14 fields, no trailing empty field
    for row in data_rows:
        w.writerow(row)     # 14 fields; csv module quotes only if a value needs it
```

Do **not** hand-build rows with `','.join('"'+v+'"' ...)` (that's how the QUOTE_ALL mistake happened
twice) — let `csv.writer` decide quoting per field. This also sidesteps the trailing-comma question
entirely: `csv.writer` never emits one.

**Before treating any template as ground truth for formatting, inspect it at the byte level** — don't
assume the file the person uploads as "the template" is itself well-formed:

```bash
python3 -c "
with open('TEMPLATE.csv','rb') as f:
    print(repr(f.read()[:200]))
    print(repr(f.read()[-60:]))
"
```

If the person has (or can get) a previously-successful filled CSV for comparison, **prioritise matching
that over the blank template** — a blank template can carry export artifacts (bad quoting, a stray
trailing comma) that were never actually required by the utility, whereas a file that's already been
accepted is ground truth for what the parser wants.

**After writing, verify three things** against the output file, not just the in-memory data:
1. `csv.reader` reports exactly 14 columns for every row, header included.
2. Re-open the raw bytes and confirm no field is unnecessarily wrapped in quotes (spot-check a numeric
   cell like a sale price — it should appear as `248.85`, not `"248.85"`).
3. The file ends with `\r\n` after the last row.
