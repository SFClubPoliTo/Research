# Generated outputs 📈

Output families remain separate by model and configuration.

| Path | Contents |
| --- | --- |
| `hft1/published-configuration` | 5000 scalar and 3000 classical multiasset Monte Carlo draws and summaries. Earlier configurations remain separately retained. |
| `hft2` | Three historical finite-lift/scalar-control cases and liquidation diagnostics. |
| `hft3/baseline_audit` | Delivered positive-baseline surface, 41 time slices across nine grid/domain configurations and interpolation diagnostics. |
| `hft3/market_sessions` | Paired E1/E2 applications of the positive scalar policy. |
| `hft3/multiasset` | Two assets/six factors each, stochastic-covariance proxy and paired risk/wealth diagnostics. |
| `validation` | Full-residual evaluation, separated refinement experiments and conditional CE bootstrap. |
| `img/publication` | Computed figures by model; `overleaf` contains exact exported historical assets. Alternative convergence curves have accompanying plotted-value CSVs. |
| `report_unificato`, `report_paper` | Complete draft TEX projects, PDFs and independent Overleaf archives. |

`src/figure_replay.py audit` verifies current computed images against the manuscript PNGs. `restore` exports exact original assets; it does not simulate them. Local report compiler by-products go to ignored `outputs/build/latex`.

Neither lower inventory risk nor a successful software replay alone establishes a CARA gain, a lower full residual, convergence, fitted P3 or measured latency.
