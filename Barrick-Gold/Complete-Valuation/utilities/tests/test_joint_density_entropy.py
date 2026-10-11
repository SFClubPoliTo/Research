"""Validate entropy coefficients, exact Poisson reduction and domain guards."""
import math
import pytest
from barrick_unified.physical_measure import restricted_joint_entropy_bound


def inputs():
    return dict(horizon=5.,variance0=.04,kappa_q=2.,theta_q=.04,xi=.2,
                rho=-.3,eta_price=1.,eta_variance=.5)


def test_identity_change_has_zero_relative_entropy():
    args=inputs();args.update(eta_price=0.,eta_variance=0.)
    result=restricted_joint_entropy_bound(**args)
    assert result['entropy_upper_bound']==0.
    assert result['log_entropy_upper_bound'] is None


def test_marked_poisson_reduces_to_exact_known_relative_entropy():
    args=inputs();args.update(eta_price=0.,eta_variance=0.,lambda0=.7,
                             intensity_ratio=1.4,mark_tilt=2.,mark_std=.1)
    result=restricted_joint_entropy_bound(**args)
    exact=5*.7*(1.4*math.log(1.4)-1.4+1+.5*1.4*2**2*.1**2)
    assert result['entropy_upper_bound']==pytest.approx(exact)


def test_bound_retains_correlated_brownian_norm_and_rejects_invalid_map():
    args=inputs();result=restricted_joint_entropy_bound(**args)
    gamma=.5*(1-2*(-.3)*.5+.5**2)/(1-.3**2)
    expected=gamma*(.04*5+.5*2*.04*25)
    assert result['entropy_upper_bound']==pytest.approx(expected)
    args['eta_variance']=11.
    with pytest.raises(ValueError,match='physical mean reversion'):
        restricted_joint_entropy_bound(**args)


def test_nonstationarity_is_distinct_from_finite_horizon_density():
    result=restricted_joint_entropy_bound(**inputs(),lambda0=1.,baseline=1.,
                                         alpha=2.,beta=1.,mark_std=.1)
    assert math.isfinite(result['log_entropy_upper_bound'])
    assert result['empirical_or_discrete_likelihood_admission'] is False
