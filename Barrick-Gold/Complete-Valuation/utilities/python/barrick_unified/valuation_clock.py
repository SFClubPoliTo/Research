"""Calendar contract for future cash flows, independent of frozen scenario runs.

Quarter-stub fractions describe elapsed time only. They are never used to
prorate production, sales or cash flow without an explicit operating model.
"""
from dataclasses import dataclass
from datetime import date, timedelta
import math
import numpy as np


def _date(value):
    if isinstance(value, date):
        return date(value.year, value.month, value.day)
    return date.fromisoformat(value)


@dataclass(frozen=True)
class FutureQuarter:
    quarter: str
    period_start: date
    future_start: date
    period_end_exclusive: date
    days_remaining: int
    calendar_fraction_remaining: float
    endpoint_years_from_valuation: float


def future_quarters(valuation_date, last_quarter_end):
    """Return future quarter intervals [start, end), ACT/365.25 endpoints.

    valuation_date is an end-of-day cutoff. The next day begins the remaining
    cash-flow interval. last_quarter_end must be a calendar quarter's last day.
    """
    cutoff = _date(valuation_date)
    horizon = _date(last_quarter_end)
    if horizon <= cutoff or (horizon+timedelta(days=1)).day != 1 or horizon.month not in [3,6,9,12]:
        raise ValueError('horizon must be a future calendar quarter end')
    remaining_start = cutoff+timedelta(days=1)
    start = date(remaining_start.year, 3*((remaining_start.month-1)//3)+1, 1)
    result = []
    while start <= horizon:
        end = date(start.year+1, 1, 1) if start.month == 10 else date(start.year, start.month+3, 1)
        admitted_start = max(start, remaining_start)
        remaining = (end-admitted_start).days
        result.append(FutureQuarter(f'{start.year}Q{(start.month-1)//3+1}', start,
                      admitted_start, end, remaining, remaining/(end-start).days,
                      ((end-timedelta(days=1))-cutoff).days/365.25))
        start = end
    return result


def discount_dated_cashflows(cashflows, payment_dates, *, valuation_date,
                             annual_effective_discount_rates):
    """Discount explicitly timed flows using caller-supplied zero rates.

    Rates are annual effective discount rates from valuation to each payment,
    not one-period stochastic WACC increments. Cash-flow/rate risk consistency
    and the equity bridge are not established by this arithmetic function.
    """
    cutoff = _date(valuation_date)
    dates = [_date(value) for value in payment_dates]
    if not dates or any(value <= cutoff for value in dates) or any(b <= a for a,b in zip(dates,dates[1:])):
        raise ValueError('strictly increasing future payment dates required')
    flows = np.asarray(cashflows, dtype=float)
    rates = np.asarray(annual_effective_discount_rates, dtype=float)
    if flows.ndim not in [1,2] or flows.shape[-1] != len(dates) or rates.shape != (len(dates),):
        raise ValueError('cash-flow final dimension and zero-rate vector must match dates')
    if not np.isfinite(flows).all() or not np.isfinite(rates).all() or (rates <= -1).any():
        raise ValueError('finite cash flows and annual rates greater than -1 required')
    times = np.array([(value-cutoff).days/365.25 for value in dates])
    discount = np.exp(-np.log1p(rates)*times)
    return np.sum(flows*discount, axis=-1)
