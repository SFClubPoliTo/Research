"""Analytical marks must preserve the conditional Euler observation law."""
import numpy as np
import pytest
from scipy.special import logsumexp
from scipy.stats import poisson, norm

from barrick_unified.physical_filter import physical_filter


def test_zero_jump_filter_is_identical():
    q=dict(kappa=2.,theta=.04,xi=.2,rho=-.5)
    args=([.01,-.02,.005],[1/252]*3,[.02]*3,q,[1.,0.,0.,0.])
    ordinary=physical_filter(*args,particles=128,substeps=4,seed=77)
    integrated=physical_filter(*args,particles=128,substeps=4,seed=77,integrate_marks=True)
    assert ordinary==integrated


def test_one_step_matches_compound_poisson_normal_mixture():
    # rho=0 makes first-step variance deterministic in the observation law.
    q=dict(kappa=2.,theta=.04,xi=.2,rho=0.,lambd=2.,mu_J=-.1,sigma_J=.2)
    h=.2; y=-.05; rate=.02; n=np.arange(30)
    mean=(rate-.5*q['theta']-q['lambd']*np.expm1(q['mu_J']+.5*q['sigma_J']**2))*h+n*q['mu_J']
    variance=q['theta']*h+n*q['sigma_J']**2
    exact=-logsumexp(poisson.logpmf(n,q['lambd']*h)+norm.logpdf(y,mean,np.sqrt(variance)))
    estimate=physical_filter([y],[h],[rate],q,[0.,0.,0.,0.],particles=100000,
                             seed=37,integrate_marks=True)
    assert abs(estimate-exact)<.01
    integrated=physical_filter([y],[h],[rate],q,[0.,0.,0.,0.],particles=32,
                               seed=37,integrate_poisson_counts=True)
    assert abs(integrated-exact)<1e-10


def test_count_integration_rejects_hawkes_excitation():
    q=dict(kappa=2.,theta=.04,xi=.2,rho=0.,alpha=.1,beta=1.,lambda_bar=.2)
    with pytest.raises(ValueError,match='constant Poisson'):
        physical_filter([.01],[1/252],[.02],q,[0.,0.,0.,0.],
                        integrate_poisson_counts=True)
