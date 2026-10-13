# Complete Valuation

One shared code and data infrastructure for the full unified study and the condensed Barrick Paper. Both editions use the same dated input freezes and generated evidence.

```text
Complete-Valuation/
|-- data/{raw,processed}/
|-- outputs/
|   |-- img/
|   |-- parameters/
|   |-- physical_measure/     # dated JSON/CSV experiments
|   |-- report_unificato/
|   `-- report_paper/
|-- src/
`-- README.md
```

Other dated output families are explained in [the output index](outputs/README.md).
Python dependency and project metadata files remain at the root. Both report
editions use the same executable infrastructure.

| Folder | Contents |
| --- | --- |
| `data/raw` | Original source freezes; `ib_local/` and `lse_local/` are local only and excluded from Git. |
| `data/processed` | Shared dated model inputs, configurations and frozen input manifests. |
| `outputs/img` | Generated figures and shared publication assets. |
| `outputs/parameters` | Fitted-coefficient output namespace. Frozen imported calibration inputs retain their original provenance under `data/processed`. |
| `outputs/physical_measure` | Physical-estimation, convergence, basis and OOS experiments. |
| `outputs/report_unificato` | Full report sources, PDF and standalone Overleaf archive. |
| `outputs/report_paper` | Condensed report sources, PDF and standalone Overleaf archive. |
| `src` | Operational Python modules, five workflow notebooks, valuation runners and generators for report figures and tables. |
| `outputs/research_notes` | Methodological documentation accompanying the published experiments. |

## Commands

Run commands from this directory, using Python 3.11 or later. Install `requirements.txt`; the local acquisition adapter also requires an authorized running IB API session.

```powershell
python -B src/main.py status
python -B src/main.py run paper-audit
python -B src/main.py run gold-basis
python -B src/main.py run copper-history
python -B src/main.py run gold-physical-oos
python -B src/main.py run physical-refit --run-id my-refit --models heston --particles 512 --substeps 16
python -B src/main.py run physical-origins
python -B src/main.py run physical-gbm-oos --run-id my-gbm-origin-panel
python -B src/main.py run physical-heston-oos --run-id my-heston-origin --origins 2026-07-10
python -B src/tools/package_report.py unificato
python -B src/tools/package_report.py paper
```

The status command audits repository structure. It does not certify a forecasting model or valuation. Acquisition and physical diagnostics require their exact local licensed input freezes; the offline suite and public aggregates remain separately reproducible. Start with `src/00_Overview.ipynb`, then follow the numbered notebooks for data/basis, Q options, P estimation/OOS, and valuation/reports. Shared executable logic lives in `src`; notebooks do not duplicate numerical implementations.

## Reports and scientific interpretation

[Unified report](outputs/report_unificato/Articolo.pdf) | [Paper](outputs/report_paper/Articolo.pdf). Compile `Articolo.tex` from the respective report directory. Its figures resolve to the common `outputs/img/publication` store. The corresponding `Articolo.zip` copies those assets into a self-contained Overleaf delivery; it contains no executable code or raw market observations.

Option repricing tests a pricing function defined under Q; the observed evolution of option surfaces occurs under P. Physical commodity prediction is evaluated under P and must be mapped to realized selling prices and accounting before entering a corporate DCF. Changing WACC does not change the probability measure. GLD USD/share, gold USD/oz and delivery-specific copper futures USD/lb retain separate units and economic identities.

The frozen valuation runners reproduce conditional operating proxies. They do not represent a validated physical corporate valuation. Fixed-current-Q particle fits are in-sample conditional experiments; their optimizer status, resolution and independent seed checks are retained. The historical P-only gold benchmark is distinct and shows interval undercoverage. Copper's available delivery strip does not reconstruct historical spot or front-month futures.

Historical origin experiments recalibrate options on 30 recovered 64-contract surfaces. All four physical models now share 29 targets. Gold RMSE is 66.35/66.77/66.84/65.81 USD/oz for GBM/Heston/Bates/Bates--Hawkes, versus 66.09 for no-change. Jump-model nominal 95% intervals cover 25/29 observations. The small Hawkes RMSE advantage is descriptive; numerical sensitivity and omitted parameter/basis uncertainty remain explicit. See [the completed gold comparison](outputs/physical_measure/20261011-four-model-gold-complete/summary.json). The dated cash-flow arithmetic excludes past payments and represents the remaining quarter stub; it does not repair the corporate bridge automatically.

A [restricted finite-horizon joint-density argument](outputs/research_notes/RESTRICTED-JOINT-DENSITY.md) establishes the measure construction under explicit model and initial-state assumptions. This theoretical result does not validate the empirical fits. The remaining scientific conditions are documented in [the physical forecasting plan](outputs/research_notes/PHYSICAL-FORECAST-PLAN.md). Publication admission still requires the P/Q estimation and validation, the realized-price and FCFF bridges, attributable claims and the terminal economic assumptions. The folder title does not imply those conditions are fulfilled.

## Provenance

Frozen source manifests are preserved. `barrick_unified.layout.migrated_path` resolves their historical locations in the shared tree without editing recorded input hashes. Migration and report-package ledgers are under `data/processed/provenance`. Changes to paths are verified by offline tests, numerical replay and report text comparison; the local originals remain preserved until final delivery is verified.

Development tests, chat records, graph tooling and local review material are maintained outside this publication tree and are not uploaded. Reproducibility manifests required by the runners are under data/processed/provenance.
