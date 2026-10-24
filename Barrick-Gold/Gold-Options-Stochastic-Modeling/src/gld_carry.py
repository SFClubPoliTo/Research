"""GLD carry: the trust expense ratio as a continuous dividend yield.

GLD holds bullion and accrues a 0.40% annual sponsor fee against NAV, so its
forward is S*exp((r-q)T) with q = 0.0040, not S*exp(rT).  For every model in
this package the call price is homogeneous of degree one in (S, K), hence

    C(S, K, T; r, q) = exp(-qT) * C(S, K*exp(qT), T; r, 0).

``forward_equivalent_surface`` applies that identity once at the data layer:
strikes and prices are rescaled and implied volatility/vega are recomputed at
q = 0 on the rescaled contracts.  The vega-weighted objective, the implied
volatilities and every pricer then equal their q-consistent values exactly,
without changing pricer signatures.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from BnS import BnS


GLD_EXPENSE_RATIO = 0.0040
APPLIED_COLUMN = "dividend_yield_applied"


def forward_equivalent_surface(frame: pd.DataFrame, q: float) -> pd.DataFrame:
    """Return the q = 0 surface that is price-equivalent to yield ``q``.

    Idempotent: a frame already carrying ``dividend_yield_applied`` is
    returned unchanged when the recorded yield equals ``q`` and rejected
    otherwise.  Rows whose implied volatility cannot be inverted are dropped
    and counted in ``attrs['dividend_yield_dropped_rows']``.
    """
    q = float(q)
    if not np.isfinite(q) or q < 0.0 or q > 0.05:
        raise ValueError("dividend yield must be in [0, 5%]")
    if APPLIED_COLUMN in frame.columns:
        recorded = pd.to_numeric(frame[APPLIED_COLUMN], errors="coerce").unique()
        if len(recorded) != 1 or not np.isclose(recorded[0], q):
            raise ValueError(f"surface already carries dividend yield {recorded}, requested {q}")
        return frame.copy()

    out = frame.copy()
    out[APPLIED_COLUMN] = q
    if q == 0.0:
        return out
    growth = np.exp(q * out["T"].to_numpy(dtype=float))
    out["K_quoted"] = out["K"].to_numpy(dtype=float)
    out["price_quoted"] = out["price"].to_numpy(dtype=float)
    out["K"] = out["K_quoted"] * growth
    out["price"] = out["price_quoted"] * growth
    if "spot" in out.columns:
        spots = out["spot"].to_numpy(dtype=float)
    else:
        spots = np.full(len(out), float(frame.attrs.get("spot", np.nan)))
    iv = np.array(
        [
            BnS.implied_vol_call(p, s, k, t, r, q=0.0)
            for p, s, k, t, r in zip(out["price"], spots, out["K"], out["T"], out["rate"])
        ],
        dtype=float,
    )
    vega = np.array(
        [
            BnS.calculate_bs_vega(s, k, t, r, 0.0, v) if np.isfinite(v) else np.nan
            for s, k, t, r, v in zip(spots, out["K"], out["T"], out["rate"], iv)
        ],
        dtype=float,
    )
    out["implied_vol"] = iv
    out["vega"] = vega
    keep = np.isfinite(iv) & np.isfinite(vega)
    dropped = int((~keep).sum())
    out = out.loc[keep].reset_index(drop=True)
    out.attrs["dividend_yield_dropped_rows"] = dropped
    return out
