from datetime import date
import numpy as np
import pytest
from barrick_unified.valuation_clock import future_quarters, discount_dated_cashflows


def test_september_cutoff_excludes_elapsed_quarters_and_preserves_explicit_stub():
    quarters = future_quarters('2026-09-02', '2030-12-31')
    assert len(quarters) == 18
    first = quarters[0]
    assert first.quarter == '2026Q3'
    assert first.future_start == date(2026,9,3)
    assert first.days_remaining == 28
    assert first.calendar_fraction_remaining == 28/92
    assert first.endpoint_years_from_valuation == 28/365.25
    assert quarters[1].calendar_fraction_remaining == 1


def test_quarter_end_cutoff_does_not_include_an_empty_past_quarter():
    assert future_quarters('2026-09-30', '2026-12-31')[0].quarter == '2026Q4'
    with pytest.raises(ValueError):
        future_quarters('2026-09-02', '2030-12-30')


def test_discount_clock_uses_actual_payment_time_and_rejects_past_flows():
    values = discount_dated_cashflows([[100.,200.],[200.,400.]], ['2026-09-30','2026-12-31'],
                 valuation_date='2026-09-02', annual_effective_discount_rates=[.1,.1])
    expected = 100/1.1**(28/365.25)+200/1.1**(120/365.25)
    np.testing.assert_allclose(values, [expected,2*expected])
    with pytest.raises(ValueError, match='future'):
        discount_dated_cashflows([100.], ['2026-06-30'], valuation_date='2026-09-02',
                                annual_effective_discount_rates=[.1])
