"""Unit tests for fcff v0 (D07). Run with: pytest -q"""

import numpy as np
import pytest

from src.fcff.model import ASSUMPTIONS_V0, PARAMS_V0, build_params, fcff, linear_path


def example_params():
    """Invented numbers of the D02 example (growth years)."""
    return {"margine": [0.15] * 10, "aliquota": [0.20] * 10,
            "da": [0.04] * 5, "capex": [0.05] * 5, "nwc": [0.10] * 5,
            "reinv_rate": [0.10] * 5}


def example_paths():
    return np.array([[104, 108, 112, 116, 120, 124, 128, 132, 136, 140],
                     [102, 104, 106, 108, 110, 112, 114, 116, 118, 120]],
                    dtype=float)


def test_d02_example_table():
    nopat, reinv, flow = fcff(example_paths(), 100.0, example_params())
    expected = np.array([
        # NOPAT, Reinv, FCFF for years 1-3, path 1 then path 2
        [[12.48, 1.44, 11.04], [12.96, 1.48, 11.48], [13.44, 1.52, 11.92]],
        [[12.24, 1.22, 11.02], [12.48, 1.24, 11.24], [12.72, 1.26, 11.46]],
    ])
    got = np.stack([nopat[:, :3], reinv[:, :3], flow[:, :3]], axis=-1)
    np.testing.assert_allclose(got, expected, atol=1e-9)


def test_identity_fcff_equals_nopat_minus_reinvestment():
    nopat, reinv, flow = fcff(example_paths(), 100.0, example_params())
    np.testing.assert_allclose(flow, nopat - reinv, atol=1e-12)


def test_transition_uses_reinvestment_rate():
    nopat, reinv, _ = fcff(example_paths(), 100.0, example_params())
    np.testing.assert_allclose(reinv[:, 5:], 0.10 * nopat[:, 5:], atol=1e-12)


def test_output_shape_matches_input():
    paths = np.full((7, 10), 95.0)
    for out in fcff(paths, 93.925, PARAMS_V0):
        assert out.shape == (7, 10)


@pytest.mark.parametrize("bad_paths", [
    np.zeros((2, 10)),
    -np.ones((2, 10)),
    np.full((2, 10), np.nan),
    np.ones(10),
    np.ones((2, 9)),
])
def test_invalid_revenues_raise(bad_paths):
    with pytest.raises(ValueError):
        fcff(bad_paths, 100.0, example_params())


@pytest.mark.parametrize("base", [0.0, -1.0, float("nan")])
def test_invalid_base_revenue_raises(base):
    with pytest.raises(ValueError):
        fcff(example_paths(), base, example_params())


@pytest.mark.parametrize("tax", [-0.01, 1.01])
def test_tax_outside_unit_interval_raises(tax):
    p = example_params()
    p["aliquota"] = [tax] * 10
    with pytest.raises(ValueError):
        fcff(example_paths(), 100.0, p)


@pytest.mark.parametrize("name", ["margine", "aliquota", "da", "capex",
                                  "nwc", "reinv_rate"])
def test_missing_parameter_raises(name):
    p = example_params()
    del p[name]
    with pytest.raises(ValueError):
        fcff(example_paths(), 100.0, p)


@pytest.mark.parametrize("name", ["margine", "da", "reinv_rate"])
def test_wrong_length_raises(name):
    p = example_params()
    p[name] = list(p[name]) + [0.1]
    with pytest.raises(ValueError):
        fcff(example_paths(), 100.0, p)


def test_negative_fcff_is_not_clipped():
    p = example_params()
    p["capex"] = [0.50] * 5
    _, _, flow = fcff(example_paths(), 100.0, p)
    assert np.all(flow[:, :5] < 0)


def test_linear_path_reaches_target():
    np.testing.assert_allclose(linear_path(0.10, 0.20),
                               [0.12, 0.14, 0.16, 0.18, 0.20])


def test_v0_params_are_labelled_provisional():
    assert PARAMS_V0["status"] == "provisional"


def test_v0_year_10_equals_maturity_values():
    a = ASSUMPTIONS_V0
    assert PARAMS_V0["margine"][9] == pytest.approx(a["m_inf"])
    assert PARAMS_V0["aliquota"][9] == pytest.approx(a["tau_inf"])
    rr_inf = a["g_inf"] / a["roic_inf"]
    assert PARAMS_V0["reinv_rate"][4] == pytest.approx(rr_inf)

    paths = np.full((3, 10), 120.0) * np.linspace(1.0, 1.4, 10)
    nopat, reinv, _ = fcff(paths, a["ricavo_base"], PARAMS_V0)
    np.testing.assert_allclose(reinv[:, 9] / nopat[:, 9], rr_inf)


def test_v0_deterministic_reference_path():
    """sigma = 0 path at 4% growth; values computed independently."""
    a = ASSUMPTIONS_V0
    R = a["ricavo_base"] * np.cumprod(np.full(10, 1.04))
    nopat, reinv, flow = fcff(R[None, :], a["ricavo_base"], PARAMS_V0)
    expected_fcff = [10.8147, 11.2473, 11.6972, 12.1650, 12.6516,
                     13.1058, 13.5758, 14.0619, 14.5648, 15.0850]
    np.testing.assert_allclose(flow[0], expected_fcff, atol=1e-3)
    assert nopat[0, 0] == pytest.approx(12.5805, abs=1e-3)
    assert reinv[0, 9] == pytest.approx(2.1550, abs=1e-3)


def test_build_params_rejects_g_above_roic():
    a = dict(ASSUMPTIONS_V0, g_inf=0.25)
    with pytest.raises(ValueError):
        build_params(a)
