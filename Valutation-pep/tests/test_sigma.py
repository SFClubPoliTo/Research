from pathlib import Path

import numpy as np
import pytest
import yaml

from src.revenues.calibration import calibrate_sigma
from src.revenues.model import estimate_sigma


def test_sample_standard_deviation():
    revenues = np.exp([0., .1, .3, .6])
    assert estimate_sigma(revenues) == pytest.approx(.1)


@pytest.mark.parametrize('revenues', [[], [1, 2], [[1, 2, 3]], [1, 0, 2],
                                    [1, -1, 2], [1, np.nan, 2], [1, np.inf, 2]])
def test_invalid_history(revenues):
    with pytest.raises(ValueError):
        estimate_sigma(revenues)


def test_d04_estimate():
    root = Path(__file__).resolve().parents[1]
    cfg = yaml.safe_load((root/'config/config.yaml').read_text(encoding='utf-8'))
    report = calibrate_sigma(cfg['revenues'])
    assert report['sigma'] == pytest.approx(0.05294302584051538)
    assert report['sigma'] == pytest.approx(cfg['revenues']['sigma'])
    assert (report['start_year'], report['end_year']) == (2014, 2025)
    assert report['log_return_observations'] == 11
    assert report['ddof'] == 1
    assert report['status'] == 'provisional'


@pytest.mark.parametrize('years', [[2014, 2014, 2015], [2014, 2016, 2017], [2016, 2015, 2014]])
def test_invalid_year_sequence(tmp_path, years):
    path = tmp_path/'history.csv'
    path.write_text('Anno;Revenue\n'+'\n'.join(f'{y};100' for y in years))
    with pytest.raises(ValueError, match='consecutive'):
        calibrate_sigma(dict(historical_csv=str(path), historical_column='Revenue',
                             r0=100, sigma_status='provisional'))
