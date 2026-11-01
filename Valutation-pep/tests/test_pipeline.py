from pathlib import Path

import numpy as np
import pytest
import yaml

from src.pipeline import run_pipeline
from src.revenues.model import simulate_revenues


@pytest.fixture
def config():
    # Synthetic fixture only: do not write these parameters to the shared config.
    path = Path(__file__).resolve().parents[1] / 'config/config.yaml'
    cfg = yaml.safe_load(path.read_text(encoding='utf-8'))
    cfg['simulation']['n_paths'] = 1000
    cfg['fcff_parameters'] = {
        'margine': [.15]*10, 'aliquota': [.20]*10,
        'da': [.04]*5, 'capex': [.05]*5, 'nwc': [.10]*5,
        'reinv_rate': [.10]*5, 'status': 'provisional'}
    cfg['rates_and_terminal'].update(
        wacc_by_stage=dict(growth=.08, transition=.08, maturity=.08),
        g_terminal=.01, roic_terminal=.10, margin_terminal=.15, tax_terminal=.20)
    return cfg


def save_config(tmp_path, cfg):
    path = tmp_path / 'config.yaml'
    path.write_text(yaml.safe_dump(cfg), encoding='utf-8')
    return str(path)


@pytest.fixture
def g3_functions():
    # Test doubles, not implementations or approved signatures supplied by G3.
    def build_wacc_path(wacc_by_stage, stage_years):
        assert stage_years == dict(growth=5, transition=5, maturity=0)
        return np.full(10, .08)

    def terminal_value(revenues, fcff, wacc_terminal, terminal_parameters):
        assert wacc_terminal == .08
        return np.full(revenues.shape[0], 100.)  # TV at H, not discounted

    def bridge(ev, bridge_parameters):
        equity = ev + sum(item['value']*item['sign'] for item in bridge_parameters['items'])
        return dict(equity_value=equity, share_price=equity/bridge_parameters['diluted_shares'])

    return dict(build_wacc_path=build_wacc_path, compute_terminal_value=terminal_value,
                compute_equity_and_price=bridge)


def test_sigma_zero_reproduces_deterministic_dcf(tmp_path, config, g3_functions):
    # Analytic synthetic benchmark; D07 reference remains pending.
    result = run_pipeline(save_config(tmp_path, config), override_sigma=0., g3_functions=g3_functions)
    revenues = 93.925 * 1.04**np.arange(1, 11)
    nopat = revenues * .15 * .8
    reinvest = np.r_[revenues[:5]*.01 + np.diff(np.r_[93.925, revenues[:5]])*.1, nopat[5:]*.1]
    discounts = 1.08**-np.arange(1, 11)
    expected_ev = (nopat-reinvest) @ discounts + 100.*discounts[-1]
    expected_price = (expected_ev - 35.) / 1.38
    np.testing.assert_allclose(result['revenues_matrix'], np.tile(revenues, (1000, 1)))
    np.testing.assert_allclose(result['prices_array'], expected_price)
    assert result['ev_mean'] == pytest.approx(expected_ev)
    assert result['price_mean'] == pytest.approx(result['price_median'])


def test_monte_carlo_revenue_mean_matches_expected_trajectory(config):
    cfg = config['revenues']
    growth = np.asarray(cfg['g_path'])
    revs = simulate_revenues(cfg['r0'], growth, cfg['sigma'], 10000, 42)
    expected = cfg['r0'] * np.cumprod(1.+growth)
    standard_errors = np.std(revs, axis=0, ddof=1) / np.sqrt(revs.shape[0])
    assert np.all(np.abs(revs.mean(axis=0)-expected) < 3.*standard_errors)


@pytest.mark.parametrize('section', ['meta', 'fcff_parameters'])
def test_final_run_blocks_provisional_data(tmp_path, config, g3_functions, section):
    config['meta']['status'] = config['fcff_parameters']['status'] = 'real'
    config[section]['status'] = 'provisional'
    with pytest.raises(RuntimeError, match='Pipeline block'):
        run_pipeline(save_config(tmp_path, config), is_final_run=True, g3_functions=g3_functions)


def test_missing_g3_is_explicit():
    with pytest.raises(RuntimeError, match='Pending G3'):
        run_pipeline()


def test_missing_g2_vectors_are_not_silently_filled(tmp_path, config, g3_functions):
    config['fcff_parameters']['da'] = None
    with pytest.raises(ValueError, match='da is missing'):
        run_pipeline(save_config(tmp_path, config), g3_functions=g3_functions)


@pytest.mark.parametrize('key', ['margin_terminal', 'tax_terminal', 'g_terminal'])
def test_terminal_continuity(tmp_path, config, g3_functions, key):
    config['rates_and_terminal'][key] += .001
    with pytest.raises(ValueError, match='year-10'):
        run_pipeline(save_config(tmp_path, config), g3_functions=g3_functions)


def test_path_dependent_wacc_rejected(tmp_path, config, g3_functions):
    g3_functions['build_wacc_path'] = lambda **kwargs: np.full((1000, 10), .08)
    with pytest.raises(ValueError, match='shared by all paths'):
        run_pipeline(save_config(tmp_path, config), g3_functions=g3_functions)


def test_horizon_and_stage_mismatch(tmp_path, config, g3_functions):
    config['meta']['horizon_years'] = 11
    with pytest.raises(ValueError, match='10-year'):
        run_pipeline(save_config(tmp_path, config), g3_functions=g3_functions)
    config['meta']['horizon_years'] = 10
    config['rates_and_terminal']['stage_years']['growth'] = 4
    with pytest.raises(ValueError, match='5 growth'):
        run_pipeline(save_config(tmp_path, config), g3_functions=g3_functions)
