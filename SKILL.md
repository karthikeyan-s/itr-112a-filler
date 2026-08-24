---
name: itr-112a-filler
metadata:
  version: 0.5.0
  author: Karthikeyan Somanathan
description: >-
  Fill India's ITR Schedule 112A CSV template for long-term capital gains (LTCG) from equity shares and
  equity-oriented mutual funds where STT is paid. Parses mutual-fund capital-gains statements from the two
  RTAs (CAMS and KFin), mutual funds held in demat/depository form and sold via a broker/distributor
  platform (e.g. NJ-Funds, CDSL/NSDL route — distinct from the RTAs), and equity capital-gains statements
  from any broker (formats vary). Applies 31-Jan-2018 grandfathering per lot, consolidates post-2018 lots,
  and validates three ways (per-lot vs statement, vs summary sheet, vs AIS). Also derives the quarter-wise
  LTCG split for Schedule CG Item F from the same sale dates. ALWAYS use when the user mentions "112A",
  "Schedule 112A", "LTCG CSV", "grandfathering", "CAMS/KFin capital gains", "demat mutual fund",
  "depository mutual fund", "quarter-wise capital gain", "Item F", or uploads capital-gains statements
  alongside a 112A template — even without naming the schedule. Strictly LONG-TERM; short-term excluded.
---

# ITR Schedule 112A Filler

## What this does

Produces a filled Schedule 112A CSV (LTCG only) from a taxpayer's capital-gains statements, plus a
reconciliation report and a list of any items that need the user's confirmation. The 112A schedule
covers **long-term** gains on **equity shares** and **equity-oriented mutual funds** where **STT was
paid**. Everything short-term is deliberately left out — it belongs in other parts of Schedule CG.

The whole job is: read each source statement → classify every long-term lot as BE or AE → compute the
14 template columns → write the CSV → prove the totals reconcile. Getting a wrong number into a tax
return is far worse than asking one extra question, so **when a value is missing or a source looks
internally inconsistent, stop and ask the user rather than assuming.**

## Inputs the user provides

1. **The blank 112A CSV template** (header row only). Preserve its header **exactly**, byte for byte,
   including line endings — the ITR utility rejects altered headers.
2. **Mutual-fund statements — two distinct routes, don't assume CAMS/KFin cover everything:**
   - **RTA route** — from one or both RTAs: **CAMS** capital-gains `.xlsx`, **KFin** capital-gains `.xlsx`.
     See `references/mutual-funds.md`.
   - **Depository/demat route** — equity-oriented MF units held in a demat account and sold through a
     broker/distributor platform (e.g. **NJ-Funds**/NJ India Invest) rather than redeemed via the AMC/RTA
     folio. A taxpayer can hold the *same kind* of scheme both ways, and one route's statement will never
     mention the other's holdings — check AIS (below) to catch a route the user didn't think to upload.
     See `references/depository-mf.md`.
3. **Equity statements** — one or more broker capital-gains reports (PDF or xlsx). Broker formats vary;
   see `references/equity-brokers.md`.
4. **AIS** (Annual Information Statement) PDF — used to reconcile sale consideration. Ask for it if not
   provided; reconcile automatically if it is, and flag any mismatch. AIS reports the RTA and depository
   MF routes as **different SFT codes** (SFT-18-EMF(M) vs SFT-17-EMF(M)) — see `references/depository-mf.md`
   and `references/ais-reconciliation.md` for telling them apart.

A taxpayer may have any subset of these (e.g. only CAMS + one broker). Handle whatever is present, and
name in the report which sources were used.

## Core workflow

Read the reference file for each source type you actually have before parsing it. Then:

1. **Identify each uploaded file** by content, not filename. Confirm with the user which files map to
   CAMS, KFin, and which broker(s), if there's any ambiguity.
2. **Scope each lot to the right taxpayer, then extract every long-term lot.** A statement pulled via
   one person's PAN can include folios belonging to family members (see "Family / minor folios" below) —
   don't assume every row belongs to the return you're filling. Ignore short-term rows entirely for the
   CSV output, but keep short-term *totals* aside — see "Short-term byproduct" below.
3. **Classify each lot BE or AE** (see "The 31-Jan-2018 split").
4. **Compute the 14 columns** per lot — per-lot rows for BE, one consolidated row per source for AE (see
   "Row granularity" and `references/csv-format.md`). Use `scripts/grandfather.py` for the arithmetic.
5. **Write the CSV** using `csv.writer(..., quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')` — never
   hand-build quoted strings. Whole-rupee money columns, alphanumeric names (see "Name sanitisation").
   Copy the header **content** from the user's blank template, but don't trust the template's own
   formatting (quoting style, trailing commas) as correct — see "Quoting style and line endings" in
   `references/csv-format.md`. If the user has a previously-successful filled CSV for comparison, treat
   it as ground truth over the blank template.
6. **Reconcile and validate** three ways (see "Validation"). Run `scripts/validate.py` helpers.
7. **Derive the quarter-wise LTCG split** for Schedule CG Item F from the same per-lot sale dates (see
   "Quarter-wise LTCG" below and `references/quarter-wise-cg.md`). Reconcile its sum to the 112A grand
   total before presenting it.
8. **Present** the filled CSV, the reconciliation report, the quarter-wise table, and any flagged items
   needing confirmation.

## The 31-Jan-2018 split (BE vs AE)

Grandfathering (the FMV protection introduced when LTCG on equity became taxable) applies **only to lots
acquired on or before 31-Jan-2018**.

- **BE** = "Before/on Equal-to" 31-Jan-2018 → grandfathering applies (FMV floor).
- **AE** = "After Equal-to"... i.e. **after** 31-Jan-2018 → no grandfathering; plain sale − cost.

Determine the class from the **acquisition date** of each lot. Two ways this shows up:

- **Explicit purchase date** in the statement (CAMS, KFin, most brokers) → compare directly to 31-Jan-2018.
- **Only a holding period** ("No. of Days") and a sale date → compute earliest purchase = sale date −
  days. If even the *longest*-held lot lands after 31-Jan-2018, every lot is AE. (This is how the
  Integrated broker statement was handled — its max was 1,146 days before a 2025 sale, ≈ 2022, so all AE.)

If a lot's class genuinely can't be determined and it matters to the gain, **ask the user**.

## Family / minor folios — whose PAN does the gain belong to?

A CAMS or KFin statement is pulled by PAN, but that pull can surface folios belonging to **other family
members**, not just the filer — most commonly a minor child's folio, where the filer is registered as
guardian. Don't assume every row in "the" statement belongs to the return you're filling; check who each
lot actually belongs to before including or excluding it.

**Two fields matter, and they answer different questions:**
- `STATUS` (e.g. `Individual` vs `On Behalf Of Minor`) tells you the folio's *operational* holding type.
- The folio's own `PAN` field tells you which PAN the redemption is **actually recorded and reported
  under** for tax purposes. `GUARDIAN_PAN` will always equal the filer's own PAN when they're the
  guardian — that's expected and tells you nothing new; it's the plain `PAN` field you need to check.

**Decision rule:**
- **If the folio's own `PAN` field equals the filer's PAN** — i.e. no separate PAN was ever allotted to
  the minor/other holder for this folio — the redemption is recorded as the **filer's own income**.
  Include it directly in the 112A schedule like any other lot of theirs. Clubbing (Sec 64(1A)) and
  Schedule SPI do **not** apply here — there's no separate PAN-linked minor income to club; it's already
  the filer's own recorded income under their own PAN.
- **If the folio's own `PAN` field is genuinely a different PAN** — the minor/dependent has their own
  allotted PAN — that gain belongs on **their** return, not the current filer's 112A. It's out of scope
  for this filing; note it in the report rather than including or silently dropping it. Whether it then
  needs clubbing into the filer's total income via Schedule SPI is a separate question the user (or their
  CA) should resolve — don't attempt that schedule here.
- **When you can't tell which case applies from the data** (e.g. the PAN field is blank, masked, or the
  statement format doesn't expose it clearly) — **ask the user**, showing them the folio number, holder
  name, `STATUS`, and whatever PAN value is visible, rather than guessing either way. Getting this wrong
  either omits taxable income or reports someone else's income on the wrong return.

This came up for real: a CAMS statement included a folio marked `On Behalf Of Minor` for a named minor
child, but that folio's own `PAN` field was identical to the filer's — no separate minor PAN existed — so
per the user's own reading of the ITR help material it belongs in the filer's own 112A, included the same
way as any other AE lot (see "Row granularity" below for how it was consolidated).

## Row granularity

- **BE lots → one row per lot.** Grandfathering resolves per lot (the higher-of/lower-of picks a
  different basis for each), so consolidating BE lots risks a wrong total. Per-lot rows reproduce each
  statement's own LTCG exactly.
- **AE lots → one consolidated row per source.** No grandfathering means the row is just
  Σsale − Σcost, so consolidation is lossless. Use one consolidated row **per source** (CAMS-AE,
  KFin-AE, and one per broker) for traceability, each with `ISIN = INNOTREQUIRD`, `Name = CONSOLIDATED`.

## Grandfathering arithmetic

For the 14-column layout and the exact formulas, read `references/csv-format.md`. In brief, per **BE** lot:

```
col6  (Total FVC)        = round(units × sale_price)
col11 (Total FMV 31Jan18)= round(units × fmv_31jan2018)
col9  (if BE)            = min(col6, col11)
col8  (actual cost)      = purchase cost (0 if genuinely unknown — see data-quality)
col7  (cost w/o indexation) = max(col8, col9)
col13 (deductions)       = col7 + col12(expenditure, usually 0)
col14 (balance / LTCG)   = col6 − col13
```

Per **AE** consolidated row: `col6 = Σsale`, `col8 = col7 = Σcost`, `col9 = col11 = 0`, cols 4/5/10
blank, `col14 = col6 − col8`. When a broker zeroes out its bought-value column but gives a **reliable
Gain/Loss** figure, take Gain/Loss as authoritative and **derive cost = sale − gain** (don't trust the
zero). This is common; see `references/equity-brokers.md`.

`scripts/grandfather.py` implements both paths and the rounding rules — prefer it over hand arithmetic.

## Data-quality handling

Real statements have gaps and glitches. The rule is **flag it, apply the safe default, and list it for
the user to confirm** — never silently guess:

- **Missing cost on a clearly pre-2018 (BE) holding** → grandfathered cost becomes the FMV regardless of
  the true purchase price (for an appreciated stock, `max(cost, min(sale,FMV))` resolves to FMV), so
  entering `cost = 0` is tax-neutral. Apply it, but **flag the pre-2018 assumption for confirmation**.
- **No cost AND no FMV** → the gain genuinely can't be computed. **Ask the user** for that lot's cost /
  acquisition date (or the underlying broker statement).
- **Internally inconsistent broker figures** (e.g. a stated gain exceeding the sale value, or a row
  duplicating another's P&L) → don't trust the statement's computed number; recompute from first
  principles, and flag it.
- **Sale value differs from AIS by a small amount** → usually the broker reports **net of brokerage**
  while AIS is **gross**; the difference equals transaction charges. Expected — note it, don't "fix" it.

## Validation (do all three, report each)

1. **Per-lot / per-source:** for each source, `Σ(BE col14) + Σ(AE col14)` must equal that statement's own
   total LTCG-without-indexation. Ties to the rupee (allowing whole-rupee rounding).
2. **Summary-sheet:** cross-check each RTA total against the fund house's own summary sheet —
   CAMS `OVERALL_SUMMARY_EQUITY`, KFin `Summary - Equity`, "LTCG without indexation" block (FVC, cost,
   gain).
3. **AIS:** AIS sale tables report **total consideration (ST + LT)**. Confirm
   `LT consideration (Σ col6 for that source) + ST consideration = AIS table total`. For equity, tie
   **quantities** per scrip (broker net vs AIS gross differ only by brokerage). See
   `references/ais-reconciliation.md` for table structure.

Report every check with its numbers and a ✓/✗, so the user can see it tied out. If any check fails,
surface it prominently rather than burying it.

## Quarter-wise LTCG (Schedule CG Item F)

ITR-2's Schedule CG Item F needs the **same long-term gain total split across 5 fixed periods** by sale
date, for section 234C interest purposes: `01/04 to 15/06`, `16/06 to 15/09`, `16/09 to 15/12`,
`16/12 to 15/03`, `16/03 to 31/03`. This is separate manual entry in the ITR form — **not** part of the
112A CSV upload — but built from the exact same lots, so compute and report it alongside the 112A output.

Bucket **per lot by its own sale date** (don't assume a whole source falls in one quarter, even though
that's common when redemptions are batched). Use `scripts/quarter_split.py`
(`quarter_bucket`/`aggregate_by_quarter`) — it works for any FY, not just one hardcoded year. **The sum
across all 5 quarters must reconcile to the 112A CSV's grand total** — that's the check that ties Item F
back to the schedule; if it doesn't tie, recheck the sale dates before presenting either number.

See `references/quarter-wise-cg.md` for where each source's sale date lives (careful with KFin — it has
two columns both named `Date`; use the sell-leg one, not the buy-leg one already used for BE/AE).

**Default to a compact table in the conversation, not a file** — it's a handful of numbers for direct
entry into the ITR utility. Only produce a separate CSV if the user asks for one.

## Short-term byproduct (not in the CSV, but report it)

While parsing, also total the **short-term** gains you skip (equity §111A, and non-equity/debt at slab).
Don't put them in the 112A CSV, but report the totals so the user can enter them elsewhere and isn't
surprised at ITR-tool validation time. Pull them from the same summary sheets (CAMS/KFin) and the
broker's short-term section.

## Output CSV rules

Read `references/csv-format.md` for the full column spec. Essentials:

- Preserve the template's header row **exactly** (and its CRLF line endings).
- Money columns (6,7,8,9,11,12,13,14) → whole rupees. Units (4) and prices (5,10) keep decimals.
- **Name column (3): strip to alphanumeric + spaces only** — remove `, / - _ ( ) & @ .` etc., or the
  utility rejects the row. AE rows use `CONSOLIDATED`.
- AE rows: `1a = AE`, `ISIN = INNOTREQUIRD`, `Name = CONSOLIDATED`, cols 4/5/10 blank.
- A row's `col14` may be **negative** (a long-term loss) — that's valid and correctly reduces the total.

## Presenting the result

Give the user: the filled CSV (via the file-presentation tool), a compact reconciliation table (the
three validation layers with numbers), the grand-total taxable LTCG, the **quarter-wise Item F table**
(inline, reconciled to the grand total), and a clearly separated **"Please confirm"** list of any
assumptions (pre-2018 classifications, zero-cost lots, unknown-broker column mappings). Note that the
ITR utility will recompute and may differ by a few rupees due to its own rounding — that's normal.

## Reference files

- `references/csv-format.md` — the 14-column 112A spec, BE/AE rules, grandfathering formulas, examples.
- `references/mutual-funds.md` — CAMS and KFin xlsx layouts: sheets, columns, equity filter, summary sheets.
- `references/depository-mf.md` — demat/depository-held mutual funds (e.g. NJ-Funds statements): sheet
  layout, columns, how this route differs from CAMS/KFin, and its distinct AIS footprint.
- `references/equity-brokers.md` — known broker formats (per-lot with FMV; summary with Gain/Loss),
  how to read holding-period-only statements, and how to onboard an unfamiliar broker (ask when in doubt).
- `references/ais-reconciliation.md` — AIS "Sale of securities and units of mutual fund" table structure
  and the ST/LT reconciliation method.
- `references/quarter-wise-cg.md` — Schedule CG Item F quarter-wise LTCG split: the 5 fixed periods,
  where each source's sale date lives, and how it reconciles to the 112A grand total.

## Changelog

- **0.5.0** — Added the **Schedule CG Item F quarter-wise LTCG split**, derived from the same per-lot
  sale dates already used for the 112A CSV, bucketed into the 5 fixed periods
  (`01/04 to 15/06` ... `16/03 to 31/03`) and reconciled to the 112A grand total. Real case (FY2025-26):
  CAMS + KFin lots all sold 26-Jun-2025/01-Sep-2025 (both "16/06 to 15/09") and NJ-Funds/CDSL lots all
  sold 04-Mar-2026 ("16/12 to 15/03") summed to ₹2,41,463 — an exact match to the 112A CSV total, also
  independently corroborated by CAMS's own `OVERALL_SUMMARY_EQUITY` quarter columns. Added
  `references/quarter-wise-cg.md` and `scripts/quarter_split.py` (`quarter_bucket`/`aggregate_by_quarter`,
  generalised to any FY rather than hardcoded). This is separate manual entry in the ITR form, not part
  of the CSV upload, so it defaults to an inline table in the conversation — a file is only produced if
  the user asks for one. See `SKILL.md` and `references/quarter-wise-cg.md`.
- **0.4.0** — Added support for **mutual funds held in demat/depository form**, a third source distinct
  from CAMS/KFin. Real case: an NJ-Funds (NJ India Invest) `MF_ProfitAndLoss` statement carried 35 lots of
  an SBI equity scheme sold via the CDSL depository route — a scheme neither CAMS nor KFin's statements
  mentioned, because it was never redeemed through the AMC/RTA folio at all. It only surfaced because AIS's
  "Sale of securities and units of mutual fund" section carries it under a **separate SFT code**
  (**SFT-17-EMF(M)**, "...(Depository)", attributed to CDSL/NSDL) from the RTA route's **SFT-18-EMF(M)**
  ("...(RTA)", attributed to CAMS/KFin by name) — the depository name, not the broker/distributor name,
  is what appears. All 35 lots were AE (purchased 2022–2025), so this added one more consolidated AE row;
  the same per-lot mechanics apply if a depository-route statement does contain pre-2018 (BE) lots — its
  FMV/31-Jan-2018 column works exactly like CAMS/KFin's, just reading `-`/blank when grandfathering
  doesn't apply. Added `references/depository-mf.md` and cross-referenced it from "Inputs the user
  provides", the reference-files list, and the AIS SFT-code note in `references/ais-reconciliation.md`.
  All three validation layers passed, and the resulting CSV was accepted by the ITR utility. See
  `SKILL.md` and `references/depository-mf.md`.
- **0.3.0** — Fixed a scoping gap found on a real filing: a CAMS statement pulled by the filer's PAN
  included a folio for a minor child (`STATUS = On Behalf Of Minor`), which had been filtered out on the
  assumption it belonged to someone else. It didn't — the folio's own `PAN` field matched the filer's,
  meaning no distinct minor PAN existed and the income was the filer's own, not subject to clubbing/
  Schedule SPI. Added "Family / minor folios — whose PAN does the gain belong to?" with the decision rule
  (check `PAN`, not just `STATUS`) and an explicit instruction to ask the user when it can't be determined
  from the data. See `SKILL.md` and `references/mutual-funds.md`.
- **0.2.0** — Fixed CSV output format after two rounds of ITR utility rejections on a real filing.
  Root cause: writing every field quoted (`QUOTE_ALL`), copied from a blank template that turned out to
  carry that as an export artifact rather than a real requirement. First fix attempt (stripping a
  trailing comma) resolved an "extra column" error but not a follow-up "Please enter valid input on
  almost every column" error — the quoting itself was the problem, since the utility's parser doesn't
  reliably accept a quoted numeric token. Fix: always write with
  `csv.writer(..., quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')`, verified byte-for-byte against a
  filed-and-accepted CSV. See "Quoting style and line endings" in `references/csv-format.md`.
- **0.1.0** — Initial version.
