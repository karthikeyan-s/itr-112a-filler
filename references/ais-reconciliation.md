# AIS reconciliation

The AIS (Annual Information Statement) is the cross-check that the sale side of the 112A is complete and
correct. It also frequently **reveals holdings the user forgot** — e.g. shares from a broker whose
statement wasn't provided (that's exactly how missing equity scrips surfaced in the reference case).

## Where the data is

Section: **"Sale of securities and units of mutual fund"**. Under it are several numbered rows (SR. NO.),
one per reporting source, each with a detail table:

- A **depository** row (CDSL/NSDL) → can be **either listed equity shares or demat-held equity-oriented MF
  units** — check the row's own information-description text and SFT code, not just the source name (see
  "Two SFT codes for mutual funds" below). Detail columns: date of sale, security name + ISIN, security
  class, **asset type = Long/Short term**, quantity, sale price/unit, **sales consideration**, cost of
  acquisition, unit FMV, fair market value, indexed cost.
- One row per **RTA** (CAMS, KFin) → **mutual-fund units** redeemed via the AMC/RTA folio route, with a
  similar detail table.

Extract with `pdftotext -layout`. The detail rows often wrap onto two physical lines (the security name
continues below) — account for that when parsing.

## Two SFT codes for mutual funds — RTA route vs depository route

Don't assume every MF sale row uses the same SFT code — there are two, and they mean different things:

- **SFT-18-EMF(M)**, "Sale of unit of equity oriented mutual fund **(RTA)**" — the AMC/RTA folio route
  (CAMS, KFin). Information Source = the RTA itself.
- **SFT-17-EMF(M)**, "Sale of unit of equity oriented mutual fund **(Depository)**" — units held in demat
  form and sold through a broker/distributor platform (e.g. NJ-Funds). Information Source = the
  **depository** (CDSL/NSDL), **never** the broker/distributor's name. See `depository-mf.md` for the full
  treatment of this route, including a worked example.

A depository row with an **EMF(M)** suffix and "...mutual fund (Depository)" wording is the MF case;
a depository row without that wording (plain company name + ISIN, no "mutual fund") is ordinary listed
equity shares — see `equity-brokers.md` instead. Match a depository-route MF row to its source statement
by **scheme name/ISIN and sale amount**, since the source name won't help.

## The key reconciliation fact

**AIS reports total sale consideration (short-term + long-term together).** Schedule 112A carries only
the long-term slice. So do **not** expect AIS's figure to equal the 112A col6 total directly. Instead:

```
LT consideration (Σ col6 for that source) + ST consideration (that source's short-term sales) = AIS table total
```

Confirm that identity per source. The short-term consideration is the same one you set aside for the ST
byproduct, so this ties the whole picture together.

## Equity specifics

- The depository table mixes **Long term** and **Short term** rows (asset-type column). For 112A, use
  the **Long term** rows; quantities per scrip must match the broker statement exactly.
- AIS shows **gross** sale prices; broker statements are often **net of brokerage**. So per-scrip rupee
  values differ by the transaction charges — expected. **Tie on quantity**, and check that
  `broker net = AIS gross − charges` roughly holds.
- AIS's own **cost / FMV columns are unreliable and often zero** — never fill 112A cost/FMV from AIS.
  Use them only as a weak hint (a populated FMV suggests a pre-2018 holding). Get real cost/FMV from the
  broker or MF statement.

## Mutual-fund specifics

- The CAMS and KFin AIS rows should tie to each RTA's **total** redemption consideration (ST + LT). The
  LT slice is what you put in 112A; the difference is the RTA's short-term redemptions.
- Small rupee differences (a few ₹) between AIS and the statement are rounding — fine.

## What to report

For each source, show: AIS table total, your LT consideration, the implied ST consideration, and a ✓ that
they add up (or a ✗ with the gap if they don't). For equity, show the per-scrip quantity tie. If AIS lists
a scrip/ISIN that appears in **no** provided statement, **flag it** — it's likely a missing broker, and
ask the user for that statement before finalising.
