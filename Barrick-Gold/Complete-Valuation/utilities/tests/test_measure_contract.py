"""Measure-boundary rejection and fixed-future drift/compensator checks."""
from pathlib import Path
import importlib.util
import numpy as np
import pytest
from barrick_unified.measure_contract import measure_contract


@pytest.mark.parametrize('law', ['P', 'Q', 'physical', 'risk_neutral'])
def test_unimplemented_valuation_measures_rejected(law):
    with pytest.raises(ValueError, match='Only a conditional'):
        measure_contract(law)


def test_fixed_delivery_and_cross_delivery_mean_are_distinct():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location('measure_paths', root/'src/reference/team-8-current/path_simulation.py')
    paths = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(paths)
    n, steps, dt = 50000, 20, .05
    hp = [.08, 2., .08, .2, -.3]
    hawkes = dict(v0=.08,kappa=2.,theta=.08,xi=.2,rho=-.3,lambda0=1.3,
                  lambda_bar=1.3,branching_ratio=.2,beta=2.,mu_J=.15,sigma_J=.12)
    engines = [lambda rates: paths.simulate_gbm_paths(6.,rates,.3,dt,n,931),
               lambda rates: paths.simulate_heston_paths(6.,rates,hp,dt,n,931)[0],
               lambda rates: paths.simulate_bates_paths(6.,rates,hp+[1.3,.15,.12],dt,n,931)[0],
               lambda rates: paths.simulate_full_hawkes_paths(6.,rates,hawkes,dt,n,931)[0]]
    for engine in engines:
        fixed = engine(np.zeros(steps))[:, -1]
        assert abs(fixed.mean()-6.) < 5*fixed.std(ddof=1)/np.sqrt(n)
        scenario = engine(np.full(steps,.12))[:, -1]
        np.testing.assert_allclose(scenario, fixed*np.exp(.12),rtol=2e-14,atol=2e-14)
    assert measure_contract()['q_to_p_change_of_measure']=='NOT_IMPLEMENTED'


def test_option_oos_does_not_admit_physical_dcf():
    contract = measure_contract()
    targets = contract["validation_targets"]
    assert targets["option_repricing"]["physical_price_validation"] is False
    assert targets["commodity_forecast"]["status"] == "NOT_IMPLEMENTED"
    assert targets["barrick_cash_flow_forecast"]["status"] == "NOT_VALIDATED"
    assert contract["corporate_valuation_ready"] is False
    assert contract['separate_physical_research']['used_in_this_valuation_operator'] is False
