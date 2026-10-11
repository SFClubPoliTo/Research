import numpy as np
import pytest
from barrick_unified.physical_filter import physical_filter


@pytest.mark.parametrize('substeps',[1,2,8])
def test_near_deterministic_variance_reduces_to_gaussian_likelihood(substeps):
    r=np.array([.01,-.02,.005]);dt=np.full(3,1/252);carry=np.full(3,.03)
    q=dict(kappa=2.,theta=.04,xi=1e-12,rho=0.)
    eta=.6
    expected=.5*np.sum(np.log(2*np.pi*.04*dt)+(r-(carry+(eta-.5)*.04)*dt)**2/(.04*dt))
    actual=physical_filter(r,dt,carry,q,[eta,0,0,0],particles=128,substeps=substeps)
    assert actual==pytest.approx(expected,abs=1e-8)


def test_zero_jump_model_is_invariant_to_jump_premia():
    r=np.array([.01,-.02,.005]);dt=np.full(3,1/252);carry=np.zeros(3)
    q=dict(kappa=2.,theta=.04,xi=.1,rho=-.2,lambd=0.,mu_J=-.03,sigma_J=.1)
    a=physical_filter(r,dt,carry,q,[0,0,0,0],particles=128)
    b=physical_filter(r,dt,carry,q,[0,0,2,3],particles=128)
    assert a==b


def test_physical_explosion_rejected():
    q=dict(kappa=2.,theta=.04,xi=.1,rho=0.,lambda_bar=.2,alpha=.8,beta=1.)
    with pytest.raises(ValueError):physical_filter([0],[.1],[0],q,[0,0,1,0])
