"""Dated operating-proxy valuation on the calendar of ``valuation_clock``.

Replaces, for runs dated 24 October 2026 onwards, the legacy convention of
``valuation.simulate_valuation_from_gold_paths`` (kept unchanged for replay):

* only quarters after the valuation date enter; Barrick actuals for quarters
  that ended before it are excluded, and the quarter that contains the
  valuation date contributes its remaining calendar fraction (registered
  assumption A-OPS-STUB: uniform intra-quarter production and unit cost);
* revenue uses the average simulated daily gold price over each quarter's
  remaining interval, not the quarter-end point;
* each flow is discounted from the midpoint of its remaining interval with a
  piecewise-constant annual WACC path whose first year is ``wacc_0``;
* the terminal value is set at the horizon end on the last four quarters.

The gold drift is the integral-preserving forward curve of the Treasury NSS
fit.  Read as a physical scenario it assumes no gold risk premium (forward
unbiased); the option-implied volatility shape remains the declared,
non-validated conditional bridge.  A risk-free (Q-consistent) discounting of
the explicit flows is reported beside the WACC result for comparison.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import math

import numpy as np

from .valuation import ValuationInputError, ValuationInputs
from .valuation_clock import FutureQuarter, future_quarters


DAYS_PER_YEAR = 365.25


def _quarter_label(start: date) -> str:
    return f"{start.year}Q{(start.month - 1) // 3 + 1}"


def _quarter_start(label: str) -> date:
    year, quarter = int(label[:4]), int(label[-1])
    return date(year, 3 * (quarter - 1) + 1, 1)


@dataclass(frozen=True)
class DatedSchedule:
    valuation_date: date
    quarters: tuple[FutureQuarter, ...]
    operating_index: np.ndarray
    remaining_fraction: np.ndarray
    start_day: np.ndarray
    end_day: np.ndarray
    flow_years: np.ndarray
    horizon_days: int
    excluded_quarters: tuple[str, ...]

    @property
    def horizon_years(self) -> float:
        return self.horizon_days / DAYS_PER_YEAR

    @property
    def rate_years(self) -> int:
        return math.ceil(self.horizon_years)


def build_schedule(valuation_date: str, horizon_end: str, first_operating_quarter: str,
                   operating_status: list[str]) -> DatedSchedule:
    """Map the base operating vector onto the quarters still to come."""
    cutoff = date.fromisoformat(valuation_date)
    quarters = tuple(future_quarters(cutoff, horizon_end))
    first = _quarter_start(first_operating_quarter)
    labels = []
    start = first
    for _ in operating_status:
        labels.append(_quarter_label(start))
        start = date(start.year + 1, 1, 1) if start.month == 10 else date(start.year, start.month + 3, 1)
    index = []
    for quarter in quarters:
        if quarter.quarter not in labels:
            raise ValuationInputError(f"no operating input for {quarter.quarter}")
        position = labels.index(quarter.quarter)
        if str(operating_status[position]).startswith("ACTUAL"):
            raise ValuationInputError(f"{quarter.quarter} is an actual quarter after the valuation date")
        index.append(position)
    excluded = tuple(label for position, label in enumerate(labels) if position not in index)
    start_day = np.array([(q.future_start - cutoff).days for q in quarters])
    end_day = np.array([(q.period_end_exclusive - cutoff).days for q in quarters])
    return DatedSchedule(
        valuation_date=cutoff,
        quarters=quarters,
        operating_index=np.asarray(index),
        remaining_fraction=np.array([q.calendar_fraction_remaining for q in quarters]),
        start_day=start_day,
        end_day=end_day,
        # Day offset d spans [(d-1)/Y, d/Y]; flows accrue evenly, so each is
        # timed at the midpoint of its remaining interval.
        flow_years=0.5 * ((start_day - 1) + (end_day - 1)) / DAYS_PER_YEAR,
        horizon_days=int(end_day[-1] - 1),
        excluded_quarters=excluded,
    )


def nss_zero_rate(nss: dict[str, float], years: np.ndarray) -> np.ndarray:
    t = np.maximum(np.asarray(years, dtype=float), 1e-6)
    x1, x2 = t / nss["tau1"], t / nss["tau2"]
    l1 = (1.0 - np.exp(-x1)) / x1
    l2 = (1.0 - np.exp(-x2)) / x2
    return nss["beta0"] + nss["beta1"] * l1 + nss["beta2"] * (l1 - np.exp(-x1)) + nss["beta3"] * (l2 - np.exp(-x2))


def daily_forward_rates(nss: dict[str, float], horizon_days: int) -> np.ndarray:
    """Integral-preserving one-day forward rates from the NSS zero curve."""
    edges = np.arange(horizon_days + 1) / DAYS_PER_YEAR
    integrated = edges * nss_zero_rate(nss, edges)
    integrated[0] = 0.0
    return np.diff(integrated) * DAYS_PER_YEAR


@dataclass(frozen=True)
class DatedResult:
    quarterly_price_usd_per_oz: np.ndarray
    quarterly_fcff_usd_mn: np.ndarray
    rate_path: np.ndarray
    pv_explicit_usd_mn: np.ndarray
    pv_explicit_risk_free_usd_mn: np.ndarray
    pv_terminal_usd_mn: np.ndarray
    enterprise_value_proxy_usd_mn: np.ndarray


def wacc_paths(inputs: ValuationInputs, shocks: np.ndarray, years: int) -> np.ndarray:
    """Annual WACC for years [0,1), [1,2), ...; year 0 is ``wacc_0``."""
    if shocks.shape[1] != years - 1:
        raise ValuationInputError("WACC shocks must cover every year after the first")
    path = np.empty((shocks.shape[0], years))
    path[:, 0] = inputs.wacc_0
    reversion = np.exp(-inputs.wacc_reversion)
    std = inputs.wacc_volatility * np.sqrt((1.0 - np.exp(-2.0 * inputs.wacc_reversion)) / (2.0 * inputs.wacc_reversion))
    for year in range(1, years):
        path[:, year] = inputs.wacc_long_run + (path[:, year - 1] - inputs.wacc_long_run) * reversion + std * shocks[:, year - 1]
    return np.clip(path, inputs.stable_growth + inputs.terminal_spread_floor, 0.25)


def discount_factors(rates: np.ndarray, years: np.ndarray) -> np.ndarray:
    """exp(-integral of log(1+w)) for piecewise-constant annual rates."""
    log_rates = np.log1p(rates)
    out = np.empty((rates.shape[0], years.size))
    for column, t in enumerate(years):
        whole = int(np.floor(t))
        accumulated = log_rates[:, :whole].sum(axis=1) + log_rates[:, min(whole, rates.shape[1] - 1)] * (t - whole)
        out[:, column] = np.exp(-accumulated)
    return out


def value_dated(inputs: ValuationInputs, schedule: DatedSchedule, daily_paths: np.ndarray,
                wacc_shocks: np.ndarray, nss: dict[str, float],
                terminal_policy: str = "signed",
                additional_quarter_margin_usd_mn: np.ndarray | None = None) -> DatedResult:
    """Value one engine's daily gold paths (time-zero column included).

    ``additional_quarter_margin_usd_mn`` holds full-quarter margins of other
    operations (copper) on the same schedule; like gold, only the remaining
    fraction of the stub quarter enters.
    """
    if daily_paths.shape[1] != schedule.horizon_days + 1:
        raise ValuationInputError("daily paths must span the valuation horizon")
    if terminal_policy not in {"signed", "legacy_positive", "none"}:
        raise ValuationInputError("unknown terminal_policy")
    price = np.column_stack([
        daily_paths[:, a:b].mean(axis=1) for a, b in zip(schedule.start_day, schedule.end_day)
    ])
    position = schedule.operating_index
    full_quarter = (price - inputs.cost_usd_per_oz[position][None, :]) * inputs.production_koz[position][None, :] / 1000.0
    if additional_quarter_margin_usd_mn is not None:
        if additional_quarter_margin_usd_mn.shape != full_quarter.shape:
            raise ValuationInputError("additional margins must align with the dated schedule")
        full_quarter = full_quarter + additional_quarter_margin_usd_mn
    margin = schedule.remaining_fraction[None, :] * full_quarter
    after_tax = margin * (1.0 - inputs.tax_rate)
    years = schedule.rate_years
    bucket = np.minimum(np.floor(schedule.flow_years).astype(int), years - 1)
    growth = np.linspace(inputs.high_growth, inputs.stable_growth, years)[bucket]
    roic = np.linspace(inputs.roic_high, inputs.roic_stable, years)[bucket]
    fcff = after_tax - np.maximum(after_tax, 0.0) * (growth / roic)[None, :]

    rates = wacc_paths(inputs, wacc_shocks, years)
    discount = discount_factors(rates, schedule.flow_years)
    pv_explicit = np.sum(fcff * discount, axis=1)
    risk_free = np.exp(-nss_zero_rate(nss, schedule.flow_years) * schedule.flow_years)
    pv_explicit_rf = fcff @ risk_free

    final_year = after_tax[:, -4:].sum(axis=1)
    if terminal_policy == "legacy_positive":
        final_year = np.maximum(final_year, 0.0)
    elif terminal_policy == "none":
        final_year = np.zeros_like(final_year)
    g = inputs.stable_growth
    terminal = final_year * (1.0 + g) * (1.0 - g / inputs.roic_stable) / (rates[:, -1] - g)
    pv_terminal = terminal * discount_factors(rates, np.array([schedule.horizon_years]))[:, 0]
    enterprise = pv_explicit + pv_terminal
    if not all(np.isfinite(a).all() for a in (price, fcff, enterprise, pv_explicit_rf)):
        raise FloatingPointError("dated valuation produced non-finite values")
    return DatedResult(price, fcff, rates, pv_explicit, pv_explicit_rf, pv_terminal, enterprise)
