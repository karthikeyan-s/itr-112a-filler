# Mutual-fund statements: CAMS and KFin (KFintech)

Both are RTAs (registrar & transfer agents). A taxpayer's equity-oriented mutual funds are split between
them by AMC. Each statement is an `.xlsx` with a **per-lot transaction sheet** (each redemption matched
to its purchase lots) and **summary sheets** used for validation.

**This covers the RTA/folio route only.** Some equity-oriented MF units are instead held in demat form and
sold through a broker/distributor platform (e.g. NJ-Funds) via the CDSL/NSDL depository — CAMS and KFin
statements never mention those units at all, and AIS reports them under a different SFT code. See
`references/depository-mf.md` for that route, and check AIS (below and `ais-reconciliation.md`) any time
you want to confirm CAMS+KFin is the whole picture.

For 112A, include **only equity-oriented schemes** (STT paid) and **only long-term lots**. Read the
per-lot sheet, compute holding period per lot, keep long-term ones, and split BE/AE by purchase date vs
31-Jan-2018.

Column positions can shift between statement versions — **locate columns by header text, not fixed
index.** The maps below are what was observed; verify headers at runtime.

---

## CAMS

**File:** `Cams_...capitalgains.xlsx`

**Per-lot sheet:** `TRXN_DETAILS` (data starts a few rows down; find the header row containing
`Scheme Name`). Relevant fields (locate by header):

- Asset class / `ASSET CLASS` → keep rows where it equals **`EQUITY`** (equity-oriented; STT paid).
- `STATUS` and `PAN` fields → **check these before assuming a row belongs to the filer.** CAMS pulls by
  PAN can surface folios for other family members (e.g. a minor child, `STATUS = On Behalf Of Minor`).
  The `STATUS` field alone doesn't tell you whose income it is — check the folio's own `PAN` field against
  the filer's PAN. See "Family / minor folios" in `SKILL.md` for the full decision rule; don't filter on
  `STATUS == Individual` alone, or you may silently drop income that belongs in this return.
- Scheme name, and a name/ISIN field.
- Redemption/sale date (the sell date).
- Purchase date — **determines BE/AE** (≤ 31-Jan-2018 → BE).
- Units (this lot), sale price/unit.
- `Sale cost` / sale amount → the lot's **sale consideration** (col6 source).
- `purchase cost` → actual cost (col8 source).
- `NAV As On 31/01/2018` → per-unit **FMV** (col10 source, for BE lots).
- `Long Term Without Indexation` → the lot's LTCG (use to cross-check per-lot math).
- `Short Term` → nonzero marks a short-term lot (exclude from 112A; add to ST byproduct).

**Long-term test:** holding period (sale − purchase) > 365 days, or `Short Term` == 0 with a value in the
Long Term column. Prefer computing the holding period explicitly.

**Summary sheet (validation):** `OVERALL_SUMMARY_EQUITY`. Its **"LongTermWithOutIndex"** block gives
Full Value of Consideration, Cost of Acquisition, and Capital Gain/Loss for all equity LT lots combined
— your `Σ(BE)+Σ(AE)` for CAMS must equal these. It also has the **Short Term** block for the byproduct.

---

## KFin (KFintech)

**File:** `Kfin_...capitalgains.xlsx`

**Per-lot sheet:** `Transaction_Details` (find the header row containing `Scheme Name`). Observed layout
(verify by header — there are two `Date`/`Trxn.Type` pairs, one for the buy leg and one for the sell leg):

- Scheme Name (ISIN is usually embedded in the scheme-name text, e.g. `... (INF903J01173)`).
- Buy-leg date → **determines BE/AE**.
- `Original Cost Amount` → actual cost (col8 source).
- Sell-leg date, `Units`, `Amount` (sale consideration → col6 source), `Price`.
- `Grandfathered` / `GrandFathered Cost` and FMV-related columns for BE lots.
- `Short Term` (exclude), `Long Term Without Index` (the lot's LTCG, cross-check).

**Long-term test:** same as CAMS — holding > 365 days.

**Summary sheet (validation):** `Summary - Equity`, **"Long Term Capital Gain without Indexation"** block
(Full Value Consideration, Cost of Acquisition, Gain/Loss). There's also `Summary - NonEquity` — check it;
if all zero, KFin has no debt component. Short-term totals for the byproduct come from the ST block here.

---

## Notes that bit us before (worth remembering)

- KFin equity may be **entirely long-term** (no short-term rows) — don't assume every source has both.
- CAMS AIS reconciliation: the AIS table figure is **ST + LT combined**; only the LT slice goes to 112A.
  `LT consideration + ST consideration = AIS total` (see `ais-reconciliation.md`).
- Both summary sheets state costs on the **grandfathered basis** for BE lots, so the summary "Cost of
  Acquisition" can read higher than the raw purchase cost — that's expected; it still nets to the same
  gain.
- A CAMS pull by PAN isn't automatically "only my own transactions" — it can include a minor's folio held
  under the same guardian. Filtering by `STATUS == Individual` alone will silently exclude a folio that
  actually belongs in the filer's own 112A (if the folio's own `PAN` field matches the filer, not a
  distinct minor PAN). Check `PAN`, not just `STATUS` — see "Family / minor folios" in `SKILL.md`.
