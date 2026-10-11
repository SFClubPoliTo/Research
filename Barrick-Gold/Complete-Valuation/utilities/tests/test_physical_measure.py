import numpy as np
import pytest
from numpy.polynomial.hermite import hermgauss
from barrick_unified.physical_measure import normal_jump_map, variance_map, hawkes_map, physical_total_return_drift


def test_mark_kernel_normalization_and_moments_by_quadrature():
    mu,s,c,b=-.05,.17,1.4,-1.7
    m=normal_jump_map(mu,s,c,b)
    x,w=hermgauss(50);j=mu+np.sqrt(2)*s*x;w=w/np.sqrt(np.pi)
    kernel=c*np.exp(b*j-b*mu-.5*b*b*s*s)
    assert np.sum(w*kernel)==pytest.approx(c)
    assert np.sum(w*kernel*j)/c==pytest.approx(m.mean_p)
    assert np.sum(w*kernel*np.expm1(j))/c==pytest.approx(m.compensator_p)


def test_variance_drift_matches_brownian_substitution():
    k,t,xi,eta=2.,.04,.3,-.8
    p=variance_map(k,t,xi,eta)
    for v in [.0,.01,.4]:
        assert p['kappa']*(p['theta']-v)==pytest.approx(k*(t-v)+xi*eta*v)
    assert 2*p['kappa']*p['theta']-xi**2==pytest.approx(2*k*t-xi**2)


def test_hawkes_compensator_scaling_on_same_event_history():
    c=1.3;p=hawkes_map(.7,.2,.4,2.,c)
    events=np.array([.1,.3,.8])
    for t in [.0,.2,.5,1.]:
        past=events[events<t]
        q=.2+(.7-.2)*np.exp(-2*t)+sum(.4*np.exp(-2*(t-past)))
        pp=p['lambda_bar']+(p['lambda0']-p['lambda_bar'])*np.exp(-p['beta']*t)+sum(p['alpha']*np.exp(-p['beta']*(t-past)))
        assert pp==pytest.approx(c*q)


def test_zero_jump_support_and_compensated_drift():
    j=normal_jump_map(-.04,.1,2.,-3.)
    assert physical_total_return_drift(.03,.05,.4,0.,j)==pytest.approx(.05)
    lam=.7
    drift=physical_total_return_drift(.03,.05,.4,lam,j)
    assert drift-j.intensity_ratio*lam*j.compensator_p==pytest.approx(.03+.4*.05-lam*j.compensator_q)
    p=hawkes_map(0.,0.,0.,2.,2.)
    assert p['lambda0']==p['lambda_bar']==p['alpha']==0


def test_invalid_or_nonstationary_maps_rejected():
    with pytest.raises(ValueError):normal_jump_map(0.,.1,0.,1.)
    with pytest.raises(ValueError):variance_map(1.,.04,.5,3.)
    with pytest.raises(ValueError):hawkes_map(1.,.2,.8,1.,2.)
    with pytest.raises(ValueError):normal_jump_map(float('nan'),.1,1.,1.)
def test_novikov_horizon_against_integrated_cir_riccati():
    from scipy.integrate import solve_ivp
    from barrick_unified.physical_measure import diffusion_novikov_horizon
    import math
    assert math.isinf(diffusion_novikov_horizon(2,.3,0,0,0))
    horizon=diffusion_novikov_horizon(1,2,0,1,0)
    def ode(t,b):return [.5-b[0]+2*b[0]**2]
    before=solve_ivp(ode,[0,.9*horizon],[0],rtol=1e-9,atol=1e-11)
    after=solve_ivp(ode,[0,1.01*horizon],[0],rtol=1e-9,atol=1e-11)
    assert before.success
    assert not after.success
    assert abs(after.t[-1]/horizon-1)<1e-6
