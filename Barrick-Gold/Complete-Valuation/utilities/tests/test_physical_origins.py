import numpy as np
import pandas as pd
import pytest
from barrick_unified.physical_origins import observed_origin_surface


def observations():
    n=12
    return pd.DataFrame(dict(date=['2026-07-10']*n,target_date=['2026-07-10']*n,
                             expiry=np.repeat(['2026-10-16','2026-12-18','2027-03-19'],4),
                             K=np.tile([80.,90.,110.,120.],3),T=np.repeat([.25,.5,.75],4),
                             dte=np.repeat([90.,180.,270.],4),spot=[100.]*n,price=[5.]*n,
                             rate=[.04]*n,curve_date=['2026-07-10']*n,
                             implied_vol=[.2]*n,vega=[10.]*n,conId=np.arange(n),
                             localSymbol=['GLD_CALL']*n,heston_price=[999.]*n,
                             mean_benchmark_iv=[999.]*n,common_model_support=[False]*n))


def test_forecast_fields_and_future_observations_do_not_enter_origin_inputs():
    frame=observations();expected=observed_origin_surface(frame,'2026-07-10',budget=6,minimum=6)
    changed=frame.copy();changed['heston_price']=-1e20;changed['mean_benchmark_iv']=0.
    future=changed.copy();future['date']='2026-07-13';future['target_date']='2026-07-13';future['price']=1e20
    actual=observed_origin_surface(pd.concat([changed,future]),'2026-07-10',budget=6,minimum=6)
    pd.testing.assert_frame_equal(expected,actual)
    assert 'heston_price' not in actual and len(actual)==6


def test_origin_curve_and_observation_dates_are_checked():
    frame=observations();frame.loc[0,'curve_date']='2026-07-13'
    with pytest.raises(ValueError,match='later than forecast origin'):
        observed_origin_surface(frame,'2026-07-10',budget=6,minimum=6)
    frame=observations();frame.loc[0,'target_date']='2026-07-13'
    with pytest.raises(ValueError,match='inconsistent observation date'):
        observed_origin_surface(frame,'2026-07-10',budget=6,minimum=6)


def test_dense_sampling_requires_enough_quotes_and_expiries():
    with pytest.raises(ValueError,match='insufficient'):
        observed_origin_surface(observations(),'2026-07-10')
