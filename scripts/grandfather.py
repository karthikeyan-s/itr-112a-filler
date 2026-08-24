"""
Grandfathering + 112A column arithmetic for Schedule 112A (LTCG only).

Import these helpers, or run as a CLI for quick checks. The functions return the
14 template columns in order as a list, ready to join with commas.

112A columns (1-indexed): 1a, ISIN, Name, Units, SalePrice, FVC, CostWOInd,
Cost, LowerOf6&11, FMVunit, TotFMV, Expenditure, Deductions, Balance.

Rules encoded here:
- BE lot: grandfathering. col7 = max(cost, min(FVC, TotFMV)); col14 = FVC - col7 - exp.
- AE consolidated: no grandfathering. col14 = FVC - cost - exp.
- Money columns are whole rupees; units/prices keep decimals.
- Names are sanitised to alphanumeric + spaces.
"""
from __future__ import annotations
import re

CUTOFF = "2018-01-31"  # acquisitions on/before this date are BE (grandfathered)


def sanitize_name(name: str) -> str:
    """Strip Name (col3) to alphanumeric + single spaces, per utility rules."""
    return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z0-9 ]", " ", name)).strip()


def be_row(isin: str, name: str, units: float, sale_price: float,
           cost: float, fmv_31jan2018: float, expenditure: float = 0):
    """
    Build a BE (grandfathered) per-lot row.
    cost may be 0 for an appreciated pre-2018 holding with unknown cost
    (tax-neutral, because the FMV floor dominates) - flag that upstream.
    """
    fvc = round(units * sale_price)          # col6
    tot_fmv = round(units * fmv_31jan2018)   # col11
    lower = min(fvc, tot_fmv)                 # col9
    cost = round(cost)                       # col8
    cost_wo_ind = max(cost, lower)           # col7
    exp = round(expenditure)                 # col12
    deductions = cost_wo_ind + exp           # col13
    balance = fvc - deductions               # col14
    return ["BE", isin, sanitize_name(name), _u(units), _p(sale_price),
            fvc, cost_wo_ind, cost, lower, _p(fmv_31jan2018), tot_fmv,
            exp, deductions, balance]


def ae_consolidated_row(total_sale: float, total_cost: float | None = None,
                        total_gain: float | None = None, expenditure: float = 0):
    """
    Build one consolidated AE row for a source.
    Supply EITHER total_cost OR total_gain:
      - total_cost given  -> gain derived as sale - cost.
      - total_gain given  -> cost derived as sale - gain (use when a broker's
                             bought-value is missing but Gain/Loss is reliable).
    """
    fvc = round(total_sale)                   # col6
    exp = round(expenditure)                  # col12
    if total_cost is None and total_gain is None:
        raise ValueError("Provide total_cost or total_gain")
    if total_cost is None:
        # derive cost from the authoritative gain
        balance = round(total_gain)           # col14
        cost = fvc - exp - balance            # col8 = col7
    else:
        cost = round(total_cost)              # col8 = col7
        balance = fvc - cost - exp            # col14
    return ["AE", "INNOTREQUIRD", "CONSOLIDATED", "", "",
            fvc, cost, cost, 0, "", 0, exp, cost + exp, balance]


def _u(x):
    """Units: keep decimals, trim trailing zeros."""
    return ("%f" % x).rstrip("0").rstrip(".") if isinstance(x, float) else x


def _p(x):
    """Prices/FMV: keep decimals, trim trailing zeros."""
    return ("%f" % x).rstrip("0").rstrip(".") if isinstance(x, float) else x


if __name__ == "__main__":
    # self-test against the reference case
    r = be_row("INE208A01029", "ASHOK LEYLAND LTD", 100, 248.85, 0, 126.55)
    assert r[13] == 12230, r
    ae = ae_consolidated_row(total_sale=130358, total_gain=-13717)
    assert ae[13] == -13717 and ae[7] == 144075, ae
    ae2 = ae_consolidated_row(total_sale=853716, total_cost=472800)
    assert ae2[13] == 380916, ae2
    print("grandfather.py self-test passed")
    print("BE example row :", r)
    print("AE (gain) row  :", ae)
    print("AE (cost) row  :", ae2)
