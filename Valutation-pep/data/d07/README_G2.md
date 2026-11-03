# D07 - fcff v0 (G2 -> G4)

**Date:** 28/10/2026 - **Authors:** G2 (Jacopo, Antonio) - **Status:** PROVISIONAL
**Units:** billions of USD, rates as decimals - **Years:** t = 1..10 = FY2026..FY2035

## What this is

The FCFF function that the G4 pipeline calls on every simulated revenue path,
running on provisional, labelled parameters. The real parameters arrive with
D11 (fcff v1 + base-year reconciliation, end of week 3, 8 Nov).

| File | Content |
|---|---|
| `fcff.py` | `fcff()`, `linear_path()`, `build_params()`, `ASSUMPTIONS_V0`, `PARAMS_V0` |
| `test_fcff.py` | unit tests (pytest) |
| `D02_interface_v2.md` | interface update: `reinv_rate` for years 6-10 |

## Usage

```python
from fcff import fcff, PARAMS_V0, ASSUMPTIONS_V0

nopat, reinvest, flows = fcff(ricavi, ASSUMPTIONS_V0["ricavo_base"], PARAMS_V0)
# ricavi: np.ndarray (N, 10), column 0 = FY2026
# outputs: np.ndarray (N, 10), bn USD
```

Requires Python 3.9+ and numpy; tests need pytest. Run the tests from this
folder:

```bash
pytest -q
```

## Model

- Growth, t = 1..5: `NOPAT = R m (1 - tau)`, `Reinv = R (capex - da) + (R_t - R_{t-1}) nwc`
- Transition, t = 6..10: margin and tax converge linearly to `m_inf`, `tau_inf`;
  `Reinv = rr_t NOPAT`, with `rr_t` linear from `rr_5` to `g_inf / roic_inf`
- `FCFF = NOPAT - Reinv`. No clipping: negative FCFF is returned as is.
- At year 10 the flows already equal the maturity assumptions, so G3's terminal
  value `TV = NOPAT_11 (1 - g/ROIC) / (WACC - g)` continues them without a jump.
  G3 must not subtract capex or NWC again.

## Provisional parameters (v0)

All values are PROVISIONAL except `ricavo_base`. Pages are printed pages of the
FY2025 10-K (PDF page = printed + 3).

| Parameter | v0 value | Basis | Replaced by |
|---|---|---|---|
| `ricavo_base` | 93.925 | Net revenue FY2025, p. 57 (real) | - |
| growth (for `rr_5` only) | 4% / year | placeholder | G1 D05 |
| margin, years 1-5 | 0.159 | Core op. profit 14.912 / 93.925, p. 42 | G1 D10 |
| `m_inf` | 0.155 | placeholder | D14 |
| tax, years 1-5 | 0.19 | 1.949 / 10.244, p. 57 | H10 with G3 |
| `tau_inf` | 0.20 | placeholder | H10 with G3 |
| `da` | 0.035 | D&A / revenue, FY2016-25 average | D11 |
| `capex` | 0.055 | Capex / revenue, FY2016-25 average | D11 |
| `nwc` | -0.05 | Operating NWC / revenue FY2025 (-4.668 / 93.925) | D11 (10-year pooled) |
| `g_inf` | 0.025 | placeholder | G3 |
| `roic_inf` | 0.20 | placeholder (ROIC with goodwill FY2025: 21.1%) | D14 |

`PARAMS_V0["status"] == "provisional"`: the final run must stop if the status is
not `"real"`.

## Reference output (sigma = 0 check)

Deterministic path at 4% growth from 93.925, with `PARAMS_V0`. G4's pipeline with
sigma = 0 and this revenue path must reproduce these FCFF values.

| t | FY | Revenue | NOPAT | Reinvestment | FCFF |
|---|---|---|---|---|---|
| 1 | 2026 | 97.682 | 12.581 | 1.766 | 10.815 |
| 2 | 2027 | 101.589 | 13.084 | 1.836 | 11.247 |
| 3 | 2028 | 105.653 | 13.607 | 1.910 | 11.697 |
| 4 | 2029 | 109.879 | 14.151 | 1.986 | 12.165 |
| 5 | 2030 | 114.274 | 14.717 | 2.066 | 12.652 |
| 6 | 2031 | 118.845 | 15.191 | 2.086 | 13.106 |
| 7 | 2032 | 123.599 | 15.680 | 2.105 | 13.576 |
| 8 | 2033 | 128.543 | 16.184 | 2.123 | 14.062 |
| 9 | 2034 | 133.685 | 16.704 | 2.139 | 14.565 |
| 10 | 2035 | 139.032 | 17.240 | 2.155 | 15.085 |

Reinvestment / NOPAT goes from 0.140 (year 5) to 0.125 = 0.025 / 0.20 (year 10).

## Known limits of v0

- `rr_5` is computed once from the deterministic path (option A in
  `D02_interface_v2.md`): on paths growing faster or slower than the base case,
  the reinvestment rate jumps slightly at year 6.
- Taxes are symmetric: a negative EBIT produces a tax credit. Extreme-path only
  for PepsiCo; to be decided for v1.
- These numbers are not results on PepsiCo: they only test the plumbing.
