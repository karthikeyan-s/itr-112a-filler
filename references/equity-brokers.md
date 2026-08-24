# Equity broker capital-gains statements

Equity (listed shares) come from a broker/depository capital-gains report. **Every broker has its own
format** — PDF or xlsx, per-lot or per-scrip summary, gross or net-of-brokerage prices, with or without
FMV and acquisition dates. Read the file first, map its columns, and if anything material is ambiguous,
**ask the user** rather than guessing.

For 112A, keep **long-term equity** lots only (STT paid). Exclude short-term (add to the ST byproduct).

## What you need per lot/scrip to fill 112A

- Quantity, sale consideration (col6), acquisition class BE/AE, and either:
  - for **BE**: actual cost + 31-Jan-2018 FMV per share, or
  - for **AE**: cost (or a reliable gain, from which cost = sale − gain).

If a source is missing the class (BE/AE) or the basis (cost/FMV) for a lot, and it affects the gain, stop
and ask.

## Two real formats seen (use as templates for recognising others)

### Format A — per-lot with FMV (e.g. Indbank / Indbank Merchant Banking)

- PDF, one row per lot: sale date, scrip, ISIN, quantity, **sale price net of brokerage**, a holding
  period in days, per-share **FMV as on 31-Jan-2018**, and the lot's LTCG.
- Because prices are **net of brokerage**, per-scrip rupee values won't match AIS to the paisa — the gap
  is the brokerage, and that's fine. Quantities still tie to AIS exactly.
- BE/AE from the holding period or an acquisition date. Most Format-A lots are old (BE) and grandfathered.
- Watch for **"No Purchase" / missing-cost rows**: if the holding clearly predates 31-Jan-2018, treat as
  BE with cost 0 (grandfathered to FMV, tax-neutral) and **flag the pre-2018 assumption**. If the row's
  own printed gain is impossible (exceeds sale value, or duplicates another row), don't trust it —
  recompute from FMV and flag it.

### Format B — per-scrip summary with Gain/Loss (e.g. Integrated Enterprises)

- One row per scrip: sold qty, transaction charges, **total sold value (net of charges)**, a
  **bought-value column that may read 0**, a reliable **Gain/Loss** column, and **No. of Days**.
- The zero bought-value is a display gap, not reality — the **Gain/Loss is computed against the real
  cost**. So take **Gain/Loss as authoritative** and derive `cost = sale − gain`. Do **not** treat
  bought-value 0 as cost 0 (that would massively overstate the gain).
- No acquisition dates, but **No. of Days is enough** to place lots relative to 31-Jan-2018: earliest
  purchase = sale date − max days. If that's after 31-Jan-2018, **all lots are AE** (no grandfathering),
  and the whole statement collapses to one consolidated AE row: `col6 = Σ sold value`,
  `col14 = Σ Gain/Loss`, `col8 = col6 − col14`.
- Validate each scrip's sale value against AIS (net = AIS gross − that scrip's transaction charges) and
  tie quantities exactly.

## Onboarding an unfamiliar broker

1. Extract the text/tables (for PDFs, `pdftotext -layout`; rasterise with `pdftoppm` if columns overlap).
2. Identify: is it **per-lot** or **per-scrip summary**? Are prices **gross or net** of brokerage? Is
   there an **FMV (31-Jan-2018)** column? Are there **acquisition dates** or only a **holding period**?
   Is there a trustworthy **Gain/Loss** column?
3. Map those to the 112A inputs. State the mapping you inferred in the report.
4. If the format doesn't clearly provide BE/AE class or cost basis, **ask the user** for the missing
   piece (often the cleanest fix is requesting the broker's standard capital-gains statement, which has
   dates, costs, and FMV).

## Long-term loss scrips

Equity statements often include small/penny-stock lots sold at a loss. **Include them** — a negative
col14 correctly reduces the aggregate LTCG. Omitting losses overstates taxable income.
