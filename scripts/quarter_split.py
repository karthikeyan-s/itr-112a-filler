"""
Quarter-wise LTCG split for ITR-2 Schedule CG, Item F ("Information about accrual/receipt
of capital gain"). This is separate manual entry in the ITR form, not part of the 112A CSV,
but it must reconcile to the 112A grand total (see references/quarter-wise-cg.md).

Works for any financial year - the FY-start year is inferred from each date (Apr-Dec -> same
calendar year; Jan-Mar -> previous calendar year), not hardcoded.
"""
from __future__ import annotations
from datetime import date

PERIOD_LABELS = [
    "01/04 to 15/06",
    "16/06 to 15/09",
    "16/09 to 15/12",
    "16/12 to 15/03",
    "16/03 to 31/03",
]


def quarter_bucket(d: date) -> str:
    """Return which of the 5 fixed FY sub-periods a sale date falls into."""
    fy_start_year = d.year if d.month >= 4 else d.year - 1
    periods = [
        (PERIOD_LABELS[0], date(fy_start_year, 4, 1),   date(fy_start_year, 6, 15)),
        (PERIOD_LABELS[1], date(fy_start_year, 6, 16),  date(fy_start_year, 9, 15)),
        (PERIOD_LABELS[2], date(fy_start_year, 9, 16),  date(fy_start_year, 12, 15)),
        (PERIOD_LABELS[3], date(fy_start_year, 12, 16), date(fy_start_year + 1, 3, 15)),
        (PERIOD_LABELS[4], date(fy_start_year + 1, 3, 16), date(fy_start_year + 1, 3, 31)),
    ]
    for label, start, end in periods:
        if start <= d <= end:
            return label
    raise ValueError(f"date {d} does not fall within any FY sub-period")


def aggregate_by_quarter(lots: list[tuple[date, float]]) -> dict[str, float]:
    """
    lots: list of (sale_date, gain) per long-term lot (any source - CAMS, KFin, depository/
    demat MF, equity broker - all pooled together, since Item F is a single combined figure
    per quarter, not per source).
    Returns {period_label: total_gain}, one key per PERIOD_LABELS, zero-filled if empty.
    """
    totals = {label: 0.0 for label in PERIOD_LABELS}
    for d, gain in lots:
        totals[quarter_bucket(d)] += gain
    return totals


def reconcile_to_112a(quarter_totals: dict[str, float], grand_total_112a: float, tol: float = 5):
    """Sum of all quarters must tie to the 112A CSV's grand total (Sec 14 sum)."""
    got = sum(quarter_totals.values())
    ok = abs(round(got) - round(grand_total_112a)) <= tol
    return ok, (f"Quarter-sum {round(got):,} vs 112A grand total {round(grand_total_112a):,} "
                f"{'OK' if ok else 'MISMATCH (%+d)' % (round(got) - round(grand_total_112a))}")


if __name__ == "__main__":
    # self-test against the reference case (FY2025-26)
    assert quarter_bucket(date(2025, 6, 26)) == "16/06 to 15/09"
    assert quarter_bucket(date(2025, 9, 1)) == "16/06 to 15/09"
    assert quarter_bucket(date(2026, 3, 4)) == "16/12 to 15/03"
    assert quarter_bucket(date(2025, 4, 1)) == "01/04 to 15/06"
    assert quarter_bucket(date(2026, 3, 31)) == "16/03 to 31/03"

    lots = (
        [(date(2025, 6, 26), 21558.9525)] +          # CAMS single lot
        [(date(2025, 9, 1), 6350.85)] * 20 +          # CAMS folio A, 20 lots (approx even split)
        [(date(2025, 9, 1), 4200.0)] * 12 +           # KFin, 12 lots
        [(date(2026, 3, 4), 1917.16)] * 35            # NJ-Funds/CDSL, 35 lots
    )
    totals = aggregate_by_quarter(lots)
    for label in PERIOD_LABELS:
        print(f"{label:<18}{totals[label]:>14,.2f}")
    ok, msg = reconcile_to_112a(totals, sum(g for _, g in lots))
    assert ok, msg
    print(msg)
    print("quarter_split.py self-test passed")
