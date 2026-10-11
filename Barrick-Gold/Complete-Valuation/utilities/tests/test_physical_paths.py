import math
import numpy as np
import pytest
from barrick_unified.physical_paths import simulate_physical_paths


Q=dict(v0=.04,kappa=2.,theta=.04,xi=.2,rho=-.3,lambd=.6,mu_J=-.05,sigma_J=.2)


def test_physical_price_mean_contains_brownian_and_jump_risk_premia():
    premia=[2.,0.,math.log(1.5),1.2]
    run=simulate_physical_paths('bates',Q,premia,initial_price=100.,output_times=[.25],
                                underlying_kind='spot_or_etf',n_paths=100000,steps_per_year=1,seed=718)
    mu_p_jump=-.05+1.2*.2
    kq=math.expm1(-.05+.5*.2**2);kp=math.expm1(mu_p_jump+.5*.2**2)
    drift=.04+2*.04+.6*(1.5*kp-kq)
    expected=100*math.exp(drift*.25)
    terminal=run.price_endpoints[:,0];se=terminal.std(ddof=1)/np.sqrt(len(terminal))
    assert abs(terminal.mean()-expected)<4*se
    assert run.measure=='P' and run.diagnostics['shared_origin_variance']==Q['v0']


def test_zero_q_jump_intensity_cannot_create_physical_events():
    q={**Q,'lambd':0.}
    kwargs=dict(initial_price=100.,output_times=[.1,.2],underlying_kind='spot_or_etf',
                n_paths=100,steps_per_year=252,seed=27)
    h=simulate_physical_paths('heston',q,[1.,.2,0.,0.],**kwargs)
    b=simulate_physical_paths('bates',q,[1.,.2,math.log(3.),2.],**kwargs)
    np.testing.assert_array_equal(h.price_endpoints,b.price_endpoints)
    np.testing.assert_array_equal(h.price_interval_means,b.price_interval_means)


def test_futures_cannot_be_projected_past_expiry_or_given_spot_carry():
    kwargs=dict(initial_price=5.,output_times=[1.],underlying_kind='fixed_delivery_future',
                contract_expiry_time=.25,carry_q=0.)
    with pytest.raises(ValueError,match='beyond contract expiry'):
        simulate_physical_paths('heston',Q,[1.,0.,0.,0.],**kwargs)
    kwargs.update(output_times=[.1],carry_q=.04)
    with pytest.raises(ValueError,match='zero Q price drift'):
        simulate_physical_paths('heston',Q,[1.,0.,0.,0.],**kwargs)


def test_gbm_requires_explicit_physical_drift_on_the_same_diffusion():
    kwargs=dict(initial_price=100.,output_times=[1.],underlying_kind='spot_or_etf',n_paths=100)
    with pytest.raises(ValueError,match='explicit finite physical drift'):
        simulate_physical_paths('black_scholes',{'sigma':.2},[0.,0.,0.,0.],**kwargs)
    run=simulate_physical_paths('black_scholes',{'sigma':.2},[0.,0.,0.,0.],physical_gbm_drift=.1,**kwargs)
    assert (run.price_endpoints>0).all()
