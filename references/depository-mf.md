# Depository/demat-held mutual funds (e.g. NJ-Funds)

A third route for equity-oriented MF capital gains, distinct from CAMS/KFin. Some MF units are held in
**demat form in a depository account (CDSL/NSDL)** and bought/sold through a broker or distributor
platform — like listed shares — rather than being redeemed through the AMC/RTA folio. **CAMS and KFin
statements will never mention these units at all**, because the transaction never touched the RTA. A
taxpayer can hold the very same fund house's schemes both ways (some via RTA folio, some via demat), so
don't assume "I have CAMS + KFin" is a complete picture — always cross-check against AIS (see below),
which is how a missing depository-route scheme is most likely to surface.

**File:** broker/distributor-branded, e.g. `..._ConsolidatedTaxStatement_MF_...xls` from NJ-Funds (NJ India
Invest). Other broker/distributor platforms that offer demat MF investing will have their own branding but
a similar shape — onboard an unfamiliar one the same way you'd onboard an unfamiliar equity broker (see
"Onboarding an unfamiliar broker" in `equity-brokers.md`): locate the header row by text, don't assume
fixed positions, and ask if a required field isn't there.

## Sheet layout (NJ-Funds observed structure)

The workbook typically has several sheets (`MF_Summary`, `MF_Holdings_*`, `MF_Inflow_Trxns`,
`MF_Outflow_Trxns`, `MF_DividendPayout`, `MF_ELSSStatement`, etc.) — **only `MF_ProfitAndLoss` matters for
112A.** It's a per-lot capital-gains report, laid out like CAMS/KFin: a merged two-row header, a
"Equity Oriented Schemes" section (STT paid — the only one relevant here; a similar "Debt Oriented
Schemes" section, if present, is out of scope for 112A), one row per matched lot, then `Sub Total` /
`Grand Total` rows, then a separate investor-level summary table further down.

**Locate columns by header text, not fixed index** — same rule as CAMS/KFin. Relevant fields (find the
header row containing `Scheme` / `Sale Date`):

- `Type` → keep rows where it equals **`EQUITY`** (equity-oriented, STT paid).
- `Scheme`, `ISIN`, `Folio No` — identify the holding.
- `Sale Date`, `Sale NAV`, `No Of Unit`, `Sale Amt.[A]` → the lot's **sale consideration** (col6 source).
- `Pur Date` → **determines BE/AE** (≤ 31-Jan-2018 → BE), same as any other source.
- `Pur Amt.[C]` and `Cost of Acquisition[F]` → actual cost (col8 source). These normally match; `[F]`
  is the one the statement itself uses in its own gain arithmetic, so prefer it if they ever differ.
- `Fair Market Value (NAV As on 31-Jan-2018)` and `Total Fair Market Value ... [E]` → per-unit and total
  FMV (col10/col11 source), **only populated for BE lots**. For AE lots these read `-` (literal dash, not
  blank/zero) — treat `-` the same as "not applicable", not as a numeric zero.
- `ST Gain/Loss Without Indexation[A-F]` → nonzero marks a short-term lot (exclude from 112A; add to ST
  byproduct). This statement also carries a `*ST Gain/Loss (Specified Debt)` column for Sec 50AA debt
  cases — irrelevant to the equity-oriented section.
- `LT Gain/Loss Without Indexation [A-F]` → the lot's authoritative LTCG (col14 basis; cross-check your
  own arithmetic against this, same role as CAMS's `Long Term Without Index` / KFin's
  `Long Term Without Index`).
- `LT Gain/Loss With Indexation [A–I]` → not used for 112A (indexation doesn't apply to equity-oriented
  schemes; this column is there for debt-scheme rows in the same report shape).

**Long-term test:** the statement already classifies each lot via the ST/LT gain columns — use those
directly rather than recomputing a holding period, same as trusting CAMS/KFin's own Short Term / Long Term
columns.

## Validation (two levels, same role as CAMS's/KFin's summary sheets)

1. **`Sub Total` / `Grand Total` rows** at the bottom of `MF_ProfitAndLoss` — Sale Amt, Cost of
   Acquisition, and LT Gain/Loss Without Indexation columns, for the equity-oriented section. Your
   `Σ(BE)+Σ(AE)` for this source must equal this row.
2. **Investor-level summary table** further down the same sheet (a small "Sr. No. / Investor / Gain-Loss"
   block split into Equity Oriented / Debt Oriented / Others, each with ST/LT sub-columns) — a second,
   independent cross-check of the same LT Gain/Loss Without Indexation total. If the report was pulled
   for **more than one investor** (multiple named rows in this block, not just one), treat it the same way
   as a CAMS pull surfacing a family member's folio — see "Family / minor folios" in `SKILL.md` — don't
   assume every lot in `MF_ProfitAndLoss` belongs to the filer just because the report covers them.

## AIS footprint — a *different* SFT code from CAMS/KFin

This is the detail most likely to trip you up: **the depository route does not appear under the same AIS
row type as CAMS/KFin.** In AIS's "Sale of securities and units of mutual fund" section:

- **RTA route (CAMS, KFin)** → **SFT-18-EMF(M)**, description "Sale of unit of equity oriented mutual fund
  **(RTA)**", **Information Source = the RTA itself** (`Computer Age Management Services Limited` /
  `KFin Technologies Pvt. Ltd`).
- **Depository route (NJ-Funds or similar)** → **SFT-17-EMF(M)**, description "Sale of unit of equity
  oriented mutual fund **(Depository)**", **Information Source = the depository itself**
  (`CENTRAL DEPOSITORY SERVICES(I) LIMITED` / an NSDL equivalent) — **never the broker/distributor's own
  name.** Don't search AIS for "NJ India Invest" or similar; you won't find it. Match this row to your
  depository-route statement by **scheme name/ISIN and sale amount**, not by source name.

**Don't confuse this with the equity-shares depository row.** A depository (CDSL/NSDL) row in AIS can mean
**either** listed equity shares **or** equity-oriented MF units sold via demat — both are technically
"depository" sales. Tell them apart by the row's own **information description** text, not the source
name alone: "Sale of unit of equity oriented mutual fund (Depository)" → MF units (this file);
"Sale of securities..." with a plain company/ISIN and no "mutual fund" wording → listed equity shares (see
`ais-reconciliation.md` and `equity-brokers.md` instead). The SFT code family also differs (EMF(M) suffix
marks mutual-fund units).

Reconcile the same way as any other source: `LT consideration (Σ col6) + ST consideration = AIS SFT-17-
EMF(M) table total` for that depository entry.

## Worked example (the case this was written from)

An NJ-Funds statement's `MF_ProfitAndLoss` sheet carried 35 lots of one equity-oriented scheme (SBI Contra
Fund), all purchased 2022–2025 (all **AE** — the `Fair Market Value (NAV As on 31-Jan-2018)` column read
`-` throughout, confirming no lot needed grandfathering). Sale Amt summed to ₹2,44,555, Cost of
Acquisition[F] summed to ₹1,77,455, LT Gain/Loss Without Indexation summed to ₹67,100 — all three tied
to the `Sub Total` row and to the investor-summary block. In AIS, this appeared as **SFT-17-EMF(M)**,
"...(Depository)", source `CENTRAL DEPOSITORY SERVICES(I) LIMITED`, count 35, amount ₹2,44,555 — an exact
match on both count and amount, with **no CAMS or KFin statement mentioning this scheme at all.**
