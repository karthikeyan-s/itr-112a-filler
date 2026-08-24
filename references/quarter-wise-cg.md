# Quarter-wise LTCG — Schedule CG, Item F

ITR-2's Schedule CG has an item **F, "Information about accrual/receipt of capital gain"**, where gains
are entered **quarter-wise** (used by the utility to compute section 234C advance-tax interest). This is
a separate manual-entry field in the ITR form itself — **not part of the 112A CSV upload** — but it must
be built from the exact same lots and must **reconcile to the 112A grand total**, so it belongs in this
skill's output.

The five periods (fixed, same wording every year):

```
01/04 to 15/06
16/06 to 15/09
16/09 to 15/12
16/12 to 15/03
16/03 to 31/03
```

## What goes in it

Only the **long-term** gain/loss total for each period — the same population of lots already going into
the 112A CSV (equity + equity-oriented MF, STT paid, long-term). Bucket **by each lot's own sale/
redemption date**, not by any other date (not purchase date, not statement date, not filing date).

**Compute this per lot, not per source.** It's tempting to assume "CAMS's whole total falls in one
quarter" because redemptions are often batched on one or two dates — that happened to be true in the
reference case below — but don't assume it. A source can easily have lots sold across several different
dates landing in different quarters (e.g. a SIP redeemed in tranches, or two unrelated redemptions in the
same folio months apart). Always group by actual sale date per lot, then sum.

## Where the sale date lives, per source

Same files you already parsed for the 112A CSV — reuse the same per-lot data, just also carry the sale
date and bucket by it:

- **CAMS** `TRXN_DETAILS`: the redemption-date column, header `Date` (format `%d-%b-%Y`, e.g.
  `26-Jun-2025`). Don't confuse with `Date_1` (purchase date, used for BE/AE).
- **KFin** `Trasaction_Details`: **there are two columns named `Date`** — the first (near `Fund`/`Scheme
  Name`) is the **buy leg**, the second (near `Trxn.Type`/`Units`/`Amount`, further right) is the **sell
  leg**. Locate by position relative to the sell-leg block, not by name alone, since both are literally
  `Date`. Use the sell-leg one.
- **Depository/demat route** (NJ-Funds etc.): `Sale Date` column (format `%d-%m-%Y`, e.g. `04-03-2026`) —
  see `depository-mf.md`.
- **Equity brokers**: whatever sale-date column that broker format already uses for the 112A row (see
  `equity-brokers.md`) — same date, just bucketed instead of only used for BE/AE.

## Bucketing logic

The FY runs 01-Apr to 31-Mar. Given a sale date, determine its FY-start year (Apr–Dec ⇒ same calendar
year; Jan–Mar ⇒ previous calendar year), then compare against the five fixed sub-ranges within that FY.
`scripts/quarter_split.py` implements this (`quarter_bucket(date)` returns the period label; works for any
FY, not hardcoded to one year) and aggregates a list of `(date, gain)` per-lot tuples into the five totals.

## Validation

**The unrounded sum across all 5 quarters must equal the 112A CSV's grand total (Σ col14), to within a
rupee or two of rounding** — this is the one check that ties Item F back to the 112A schedule. If it
doesn't tie, a lot's sale date was misread (or a lot was double-counted/omitted) — recheck before
presenting either figure.

Report each quarter's total rounded to the whole rupee (same convention as the 112A CSV), using the same
per-source rounded figures where a whole source's lots land in one quarter (simplest and ties exactly);
if a source's lots split across quarters, round each quarter's sub-total independently.

## Presenting the result

**Default to showing this as a compact table in the conversation, not a file.** It's a handful of numbers
the user types directly into the ITR utility's Item F fields — a CSV adds friction for no benefit here.
**Only produce a separate CSV/file if the user asks for one.**

## Worked example (the case this was written from)

FY2025-26: every CAMS lot was sold on one of two dates (26-Jun-2025, 01-Sep-2025), both landing in
"16/06 to 15/09"; every KFin lot was sold 01-Sep-2025 (same quarter); every NJ-Funds/CDSL lot was sold
04-Mar-2026, landing in "16/12 to 15/03". Result: only two of the five quarters were non-zero —
₹1,74,363 ("16/06 to 15/09" = CAMS 1,53,660 + KFin 20,703) and ₹67,100 ("16/12 to 15/03" = NJ-Funds/CDSL)
— summing to ₹2,41,463, matching the 112A CSV's grand total exactly. Independently corroborated by
CAMS's own `OVERALL_SUMMARY_EQUITY` sheet, which lays out its quarter columns the same way and shows the
entire CAMS total under "16/06 to 15/09" too.
