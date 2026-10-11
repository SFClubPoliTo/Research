import numpy as np
import pandas as pd
import pytest
from barrick_unified.gold_basis import forecast_log_basis, gld_forecast_to_gold


def test_future_prices_do_not_enter_basis_and_exact_trend_is_recovered():
    dates=pd.date_range('2020-01-01',periods=260)
    years=np.arange(260)/365.25
    frame=pd.DataFrame(dict(date=dates,gld_usd_share=100*np.exp(-.004*years),gold_midpoint_usd_oz=1000.))
    origin,target=dates[254],dates[255]
    result=forecast_log_basis(frame,origin,target)
    frame.loc[frame.date>origin,['gld_usd_share','gold_midpoint_usd_oz']]=np.nan
    assert forecast_log_basis(frame,origin,target)==result
    assert result['annual_log_ratio_trend']==pytest.approx(-.004)
    assert result['log_ratio_prediction']==pytest.approx(np.log(.1)-.004*255/365.25)


def test_conversion_units_and_order_are_preserved():
    mean,quantiles=gld_forecast_to_gold(100.,[80.,90.,100.,110.,120.],np.log(.1))
    assert mean==pytest.approx(1000.)
    np.testing.assert_allclose(quantiles,[800.,900.,1000.,1100.,1200.])
    with pytest.raises(ValueError):
        gld_forecast_to_gold(100.,[80.,110.,100.,120.,130.],np.log(.1))
