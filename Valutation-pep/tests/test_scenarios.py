from copy import deepcopy
from pathlib import Path
import zipfile

import numpy as np
import pytest
import yaml

from src.fcff.model import fcff
from src.pipeline import run_pipeline
from src.revenues.scenarios import read_scenarios, prepare_scenario

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def cfg():
    return yaml.safe_load((ROOT / 'config/config.yaml').read_text(encoding='utf-8'))


@pytest.mark.parametrize('name,first,last', [
    ('bear', 94.988156416238965, 110.97200643997608),
    ('base', 97.161996472863677, 127.01498691480568),
    ('growth', 99.277137735058517, 144.47702479656834)])
def test_workbook_and_pipeline_sigma_zero(cfg, tmp_path, name, first, last):
    original = deepcopy(cfg)
    effective, info = prepare_scenario(cfg, name)
    assert cfg == original
    revenues = cfg['revenues']['r0'] * np.cumprod(1+np.array(info['g_path']))
    assert revenues[0] == pytest.approx(first)
    assert revenues[-1] == pytest.approx(last)
    reference = read_scenarios(ROOT / cfg['revenues']['d05']['source'])
    np.testing.assert_allclose(revenues, reference['scenarios'][name]['expected_revenues'])
    # Independent option-A ratio from year-5 growth and G2 coefficients.
    p = cfg['fcff_parameters']
    g5 = info['g_path'][4]
    rr5 = (p['capex'][4]-p['da'][4] + g5/(1+g5)*p['nwc'][4]) / (p['margine'][4]*(1-p['aliquota'][4]))
    expected_rr = rr5 + np.arange(1,6)/5 * (.25-rr5)
    np.testing.assert_allclose(info['reinv_rate'], expected_rr)
    assert info['reinv_rate'] != p['reinv_rate']
    assert effective['fcff_parameters']['margine'] == p['margine']
    assert effective['fcff_parameters']['aliquota'] == p['aliquota']
    cfg['simulation']['n_paths'] = 3
    cfg['rates_and_terminal']['wacc_by_stage'] = dict(growth=.08, transition=.08, maturity=.08)
    path = tmp_path / 'config.yaml'
    path.write_text(yaml.safe_dump(cfg), encoding='utf-8')
    nopat, reinvest, flows = fcff(revenues[None,:], cfg['revenues']['r0'], effective['fcff_parameters'])
    result = run_pipeline(str(path), override_sigma=0, scenario=name)
    np.testing.assert_allclose(result['revenues_matrix'], np.tile(revenues, (3,1)))
    assert np.all(np.isfinite(result['prices_array']))
    assert result['scenario']['scenario'] == name
    assert result['sigma_calibration']['sigma'] == pytest.approx(.05294302584051538)


def test_default_base_and_validation(cfg):
    assert prepare_scenario(cfg)[1]['scenario'] == 'base'
    with pytest.raises(ValueError, match='scenario'):
        prepare_scenario(cfg, 'bull')
    cfg['rates_and_terminal']['g_terminal'] = .03
    with pytest.raises(ValueError, match='G3'):
        prepare_scenario(cfg)
    cfg['rates_and_terminal']['g_terminal'] = .025
    cfg['revenues']['r0'] = 100
    with pytest.raises(ValueError, match='base revenue'):
        prepare_scenario(cfg)


def test_final_run_still_blocks_d05_review(cfg):
    cfg['meta']['status'] = cfg['fcff_parameters']['status'] = cfg['revenues']['sigma_status'] = 'real'
    with pytest.raises(RuntimeError, match='D05'):
        prepare_scenario(cfg, is_final_run=True)


def test_stale_workbook_cache_rejected(cfg, tmp_path):
    source = ROOT / cfg['revenues']['d05']['source']
    bad = tmp_path / 'bad.xlsx'
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(bad, 'w') as dst:
        for name in src.namelist():
            data = src.read(name)
            if name == 'xl/worksheets/sheet1.xml':
                data = data.replace(b'127.01498691480568', b'999.01498691480568')
            dst.writestr(name, data)
    with pytest.raises(ValueError, match='revenue reference'):
        read_scenarios(bad)


def test_scenario_change_keeps_seed_and_sigma(cfg):
    from src.revenues.model import simulate_revenues
    paths = []
    for name in ('bear','base','growth'):
        effective, _ = prepare_scenario(cfg, name)
        g = np.array(effective['revenues']['g_path'])
        rev = simulate_revenues(93.925, g, .05, 100, 42)
        paths.append(rev / (93.925*np.cumprod(1+g)))
    np.testing.assert_allclose(paths[0], paths[1])
    np.testing.assert_allclose(paths[1], paths[2])
