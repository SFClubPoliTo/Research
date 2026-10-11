import numpy as np
import pytest
from barrick_unified.physical_gbm import fit_gbm,predictive_log_score


def test_fixed_diffusion_drift_score_equation_and_ito_term():
    r=np.array([.01,-.02,.04]);dt=np.array([1.,2.,3.])/365.25
    f=fit_gbm(r,dt,sigma_q=.2)
    assert sum(r-f.log_drift*dt)==pytest.approx(0.)
    assert f.arithmetic_drift-f.log_drift==pytest.approx(.02)
    assert f.drift_standard_error==pytest.approx(.2/np.sqrt(sum(dt)))


def test_historical_fit_recovers_synthetic_diffusion_and_drift():
    rng=np.random.default_rng(731);dt=np.full(200000,1/252)
    r=(.08-.5*.2**2)*dt+.2*np.sqrt(dt)*rng.normal(size=len(dt))
    f=fit_gbm(r,dt)
    assert abs(f.arithmetic_drift-.08)<4*f.drift_standard_error
    assert f.sigma==pytest.approx(.2,rel=.01)
    assert np.isfinite(predictive_log_score(.01,1/252,f))


@pytest.mark.parametrize('returns,gaps',[([0,1],[0,1]),([0,1],[1]),([0,float('nan')],[1,1])])
def test_invalid_history_rejected(returns,gaps):
    with pytest.raises(ValueError):fit_gbm(returns,gaps)
