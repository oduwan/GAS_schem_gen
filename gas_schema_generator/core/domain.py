from __future__ import annotations
"""Domain calculations per spec.

Formulas:
- Pmax = 1.15 * sum(Pinv_kW)
- I_est (A) = (Pmax_kW * 1000) / (230 * 3)
  (Assumes 230 V phase-to-neutral; 3-phase system)
- Direct metering if I_est < 80 A, else CT scheme.
- Per-inverter breaker: ceil_to_set(I_inv, BREAKER_SET),
  where I_inv = (Pmax_kW * 1000 * 1.15) / (230 * 3)  # per spec note
- Main breaker: direct→BREAKER_SET, CT→MCCB_SET; CT rating from CT_SET.
"""
from .config import BREAKER_SET, MCCB_SET, CT_SET
from .model import Selection


def ceil_to_set(value: float, options: list[int]) -> int:
    for o in options:
        if value <= o:
            return o
    return options[-1]


def compute_pmax_kw(powers_kw: tuple[float, ...]) -> float:
    return sum(powers_kw) * 1.15


def select_equipment(powers_kw: tuple[float, ...]) -> Selection:
    pmax_kw = compute_pmax_kw(powers_kw)
    i_est = (pmax_kw * 1000.0) / (230.0 * 3.0)
    direct = i_est < 80.0

    # NOTE: spec applies 1.15 again here for per-inverter breaker sizing.
    inv_i = (pmax_kw * 1000.0 * 1.15) / (230.0 * 3.0)
    per_inv_breaker = ceil_to_set(inv_i, BREAKER_SET)

    if direct:
        main_breaker = ceil_to_set(i_est, BREAKER_SET)
        ct = None
    else:
        main_breaker = ceil_to_set(i_est, MCCB_SET)
        ct = ceil_to_set(i_est, CT_SET)

    return Selection(pmax_kw, direct, per_inv_breaker, main_breaker, ct)