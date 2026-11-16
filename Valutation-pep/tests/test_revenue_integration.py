from copy import deepcopy
from pathlib import Path
import numpy as np
import pytest
import yaml
from src.pipeline import run_pipeline
from src.revenues.scenarios import prepare_scenario, read_scenarios

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('scenario', ['bear', 'base', 'growth'])
def test_d05_reaches_pipeline_without_changing_g2(tmp_path, scenario):
    cfg = yaml.safe_load((ROOT/'config/config.yaml').read_text())
    original = deepcopy(cfg)
    effective, info = prepare_scenario(cfg, scenario)
    assert cfg == original
    assert effective['fcff_parameters'] == cfg['fcff_parameters']
    cfg['simulation']['n_paths'] = 4
    path = tmp_path/'config.yaml'
    path.write_text(yaml.safe_dump(cfg))
    out = run_pipeline(str(path), scenario=scenario, override_sigma=0)
    delivery = read_scenarios(ROOT/cfg['revenues']['d05']['source'])
    expected = delivery['scenarios'][scenario]['expected_revenues']
    np.testing.assert_allclose(out['revenues_matrix'], np.tile(expected, (4,1)))
    assert out['scenario']['scenario'] == scenario
    assert np.all(np.isfinite(out['prices_array']))


def test_sigma_is_recalculated_and_seed_is_reproducible(tmp_path):
    cfg = yaml.safe_load((ROOT/'config/config.yaml').read_text())
    cfg['simulation']['n_paths'] = 4
    cfg['revenues']['sigma'] = .99
    path = tmp_path/'config.yaml'
    path.write_text(yaml.safe_dump(cfg))
    first = run_pipeline(str(path))
    second = run_pipeline(str(path))
    assert first['sigma_used'] == pytest.approx(.05294302584051538)
    assert first['scenario']['scenario'] == 'base'
    np.testing.assert_array_equal(first['prices_array'], second['prices_array'])


def test_invalid_scenario_and_final_run():
    with pytest.raises(ValueError, match='scenario'):
        run_pipeline(scenario='unknown')
    with pytest.raises(RuntimeError):
        run_pipeline(is_final_run=True)

@pytest.mark.parametrize('scenario,spread', [('bear',0.),('base',.015),('growth',.025)])
def test_terminal_roic_matches_g2(tmp_path, monkeypatch, scenario, spread):
    import src.pipeline as pipeline
    from src.fcff.model import build_params
    cfg = yaml.safe_load((ROOT/'config/config.yaml').read_text())
    cfg['simulation']['n_paths'] = 3
    path = tmp_path/'config.yaml'
    path.write_text(yaml.safe_dump(cfg))
    original = pipeline.compute_enterprise_value
    def checked_ev(revenues, fcff, params):
        expected_roic = cfg['fcff_parameters']['w_inf'] + spread
        assert params['roic_terminal'] == pytest.approx(expected_roic)
        assumptions = dict(cfg['fcff_parameters'], s_inf=spread)
        assert build_params(assumptions)['rr_inf'] == pytest.approx(params['g_terminal']/expected_roic)
        out = original(revenues, fcff, params)
        nopat = revenues[:,-1]*(1+params['g_terminal'])*params['margin_terminal']*(1-params['tax_terminal'])
        tv = nopat*(1-params['g_terminal']/expected_roic)/(params['wacc_maturity']-params['g_terminal'])
        np.testing.assert_allclose(out['pv_tv'],tv*out['df_vector'][-1])
        return out
    monkeypatch.setattr(pipeline,'compute_enterprise_value',checked_ev)
    result = pipeline.run_pipeline(str(path), scenario=scenario, override_sigma=0)
    assert result['roic_terminal'] == pytest.approx(cfg['fcff_parameters']['w_inf']+spread)
