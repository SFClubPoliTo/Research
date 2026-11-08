from pathlib import Path
import numpy as np
import pytest
import yaml
from src.pipeline import run_pipeline
from src.revenues.scenarios import prepare_scenario
from src.fcff.model import fcff
from src.rates.model import compute_enterprise_value


def test_d05_pipeline_matches_deterministic_valuation():
    root = Path(__file__).resolve().parents[1]
    cfg = yaml.safe_load((root / "config/config.yaml").read_text())
    cfg, info = prepare_scenario(cfg)
    r = cfg['revenues']['r0'] * np.cumprod(1 + np.array(info['g_path']))
    nopat, _, flows = fcff(r[None,:], cfg['revenues']['r0'], cfg['fcff_parameters'])
    ev = compute_enterprise_value(r[None,:], flows, cfg['rates_and_terminal'],
        nopat[:, -1] * (1 + cfg['rates_and_terminal']['g_terminal']))
    expected = (ev['ev'][0] + sum(cfg['bridge']['items'].values())) / cfg['bridge']['diluted_shares']
    result = run_pipeline(override_sigma=0)
    np.testing.assert_allclose(result['prices_array'], expected)
    assert result['sigma_calibration']['sigma'] == pytest.approx(.05294302584051538)


def test_final_run_blocks_provisional_data():
    with pytest.raises(RuntimeError):
        run_pipeline(is_final_run=True)


@pytest.mark.parametrize('sigma', [-1, float('nan')])
def test_invalid_sigma(sigma):
    with pytest.raises(ValueError):
        run_pipeline(override_sigma=sigma)
