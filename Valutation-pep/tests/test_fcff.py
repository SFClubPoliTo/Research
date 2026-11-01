import numpy as np
import pytest

from src.fcff.model import fcff


@pytest.fixture
def params():
    return {"margine": [0.15] * 10, "aliquota": [0.20] * 10,
            "da": [0.04] * 5, "capex": [0.05] * 5, "nwc": [0.10] * 5,
            "reinv_rate": [0.10] * 5, "status": "provisional"}


def test_d02_example_and_transition(params):
    revenues = np.array([[104, 108, 112, 116, 120, 124, 128, 132, 136, 140],
                         [102, 104, 106, 108, 110, 112, 114, 116, 118, 120.]])
    nopat, reinvest, flows = fcff(revenues, 100., params)
    assert nopat.shape == reinvest.shape == flows.shape == (2, 10)
    np.testing.assert_allclose(flows[:, :3], [[11.04, 11.48, 11.92], [11.02, 11.24, 11.46]])
    np.testing.assert_allclose(reinvest[:, 4], [1.60, 1.30])
    np.testing.assert_allclose(reinvest[:, 5], [1.488, 1.344])
    np.testing.assert_allclose(flows, nopat - reinvest)


@pytest.mark.parametrize("revenues", [np.ones(10), np.ones((2, 9)),
    np.zeros((2, 10)), -np.ones((2, 10)), np.full((2, 10), np.nan), np.full((2, 10), np.inf)])
def test_invalid_revenues(revenues, params):
    with pytest.raises(ValueError):
        fcff(revenues, 100., params)


@pytest.mark.parametrize("base", [0., -1., np.nan, np.inf])
def test_invalid_base(base, params):
    with pytest.raises(ValueError):
        fcff(np.ones((2, 10)), base, params)


@pytest.mark.parametrize("key", ["margine", "aliquota", "da", "capex", "nwc", "reinv_rate"])
@pytest.mark.parametrize("bad_value", [None, [1.], [np.nan] * 5, [np.inf] * 10])
def test_invalid_parameter(key, bad_value, params):
    params[key] = bad_value
    with pytest.raises(ValueError):
        fcff(np.ones((2, 10)), 100., params)


def test_missing_parameter_and_tax_bounds(params):
    for key in params:
        if key == 'status':
            continue
        incomplete = dict(params)
        del incomplete[key]
        with pytest.raises(ValueError):
            fcff(np.ones((2, 10)), 100., incomplete)
    for tax in (-0.1, 1.1):
        with pytest.raises(ValueError):
            fcff(np.ones((2, 10)), 100., dict(params, aliquota=[tax]*10))


def test_negative_nwc_fcff_and_ignored_keys(params):
    revenues = np.full((2, 10), 104.)
    nopat, reinvest, flows = fcff(revenues, 100., dict(params, nwc=[-.1]*5))
    np.testing.assert_allclose(reinvest[:, 0], .64)
    assert np.all(fcff(revenues, 100., dict(params, capex=[1.]*5, reinv_rate=[2.]*5))[2] < 0)
    expected = fcff(revenues, 100., params)[2]
    np.testing.assert_allclose(fcff(revenues, 100., dict(params, extra=42, status='ignored'))[2], expected)
