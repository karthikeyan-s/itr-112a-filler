"""
Validation helpers for the 112A filler. Three layers:
  1. per_source_check  - Σ(BE col14)+Σ(AE col14) == statement's own LTCG
  2. summary_check     - source total == fund-house summary-sheet LTCG-without-indexation
  3. ais_check         - LT consideration + ST consideration == AIS table total

Each returns (ok: bool, message: str) with the numbers spelled out, so the
message can be dropped straight into the reconciliation report.

Tolerance defaults to a few rupees to absorb whole-rupee rounding.
"""
from __future__ import annotations
import csv


def read_csv_totals(path: str):
    """Return (num_rows, total_col14) from a filled 112A CSV."""
    rows = list(csv.reader(open(path)))[1:]
    total = sum(round(float(r[13])) for r in rows if r[13].strip())
    return len(rows), total


def per_source_check(source: str, be_ltcg: float, ae_ltcg: float,
                     statement_ltcg: float, tol: int = 5):
    got = round(be_ltcg) + round(ae_ltcg)
    ok = abs(got - round(statement_ltcg)) <= tol
    return ok, (f"[{source}] BE {round(be_ltcg):,} + AE {round(ae_ltcg):,} = "
                f"{got:,} vs statement LTCG {round(statement_ltcg):,} "
                f"{'OK' if ok else 'MISMATCH (%+d)' % (got-round(statement_ltcg))}")


def summary_check(source: str, computed_total: float, summary_total: float, tol: int = 10):
    ok = abs(round(computed_total) - round(summary_total)) <= tol
    return ok, (f"[{source}] computed LTCG {round(computed_total):,} vs summary-sheet "
                f"{round(summary_total):,} "
                f"{'OK' if ok else 'MISMATCH (%+d)' % (round(computed_total)-round(summary_total))}")


def ais_check(source: str, lt_consideration: float, st_consideration: float,
              ais_total: float, tol: int = 20):
    got = round(lt_consideration) + round(st_consideration)
    ok = abs(got - round(ais_total)) <= tol
    return ok, (f"[{source}] LT {round(lt_consideration):,} + ST {round(st_consideration):,} = "
                f"{got:,} vs AIS table {round(ais_total):,} "
                f"{'OK' if ok else 'MISMATCH (%+d)' % (got-round(ais_total))}")


def quantity_tie(scrip: str, statement_qty: float, ais_qty: float):
    ok = round(statement_qty) == round(ais_qty)
    return ok, (f"[{scrip}] qty statement {statement_qty:g} vs AIS {ais_qty:g} "
                f"{'OK' if ok else 'MISMATCH'}")


if __name__ == "__main__":
    # self-test against the reference case numbers
    assert per_source_check("CAMS", 36209, 380916, 417125)[0]
    assert per_source_check("KFin", 2205, 160984, 163189)[0]
    assert summary_check("CAMS", 417125, 417125)[0]
    assert ais_check("CAMS", 912291, 342486, 1254765)[0]
    # depository/demat MF route (NJ-Funds/CDSL) — FY2025-26 real case, ITR-utility accepted
    assert per_source_check("NJFunds/CDSL", 0, 67100, 67100.45)[0]
    assert ais_check("NJFunds/CDSL (AIS SFT-17-EMF(M))", 244555, 0, 244555.00)[0]
    print("validate.py self-test passed")
