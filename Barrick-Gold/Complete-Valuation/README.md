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
| Row-level option quotes | GLD/HG option rows with IB contract ids, bid/ask or quote times (`team8_freeze` surfaces, `audit_inputs` samples and forecasts, copper calibration rows, the 24 October calibration surfaces) are licensed provider data: they are kept locally and listed in `.gitignore`. Aggregates, parameters, manifests and hashes stay public. |
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
python -B src/build_dated_paper_audit.py all      # 24 October evidence: calibration, carry, valuation, copper, OOS
python -B src/build_report_fragments.py           # numbers and figures read by both reports
python -B src/tools/package_report.py unificato
python -B src/tools/package_report.py paper
```

`paper-audit` replays the frozen 7 September chain; it and the 24 October rebuild need the local row-level option files described above. The rolling OOS of 24 October was produced with `src/pricing/oos_validation.py --dividend-yield 0.004` (equal search policy, no Hawkes-only warm start) into `data/processed/team8/oos_q040_20261024/`.

The status command audits repository structure. It does not certify a forecasting model or valuation. Acquisition and physical diagnostics require their exact local licensed input freezes; the offline suite and public aggregates remain separately reproducible. Start with `src/00_Overview.ipynb`, then follow the numbered notebooks for data/basis, Q options, P estimation/OOS, and valuation/reports. Shared executable logic lives in `src`; notebooks do not duplicate numerical implementations.

## Reports and scientific interpretation

[Unified report](outputs/report_unificato/Articolo.pdf) | [Paper](outputs/report_paper/Articolo.pdf). Compile `Articolo.tex` from the respective report directory. Its figures resolve to the common `outputs/img/publication` store, and both editions read their numbers from the same generated file (`generated/results_20261024.tex`). `src/tools/package_report.py` writes a self-contained Overleaf `Articolo.zip` next to each PDF; the archives are build products and are not tracked in Git.

Option repricing tests a pricing function defined under Q; the observed evolution of option surfaces occurs under P. Physical commodity prediction is evaluated under P and must be mapped to realized selling prices and accounting before entering a corporate DCF. Changing WACC does not change the probability measure. GLD USD/share, gold USD/oz and delivery-specific copper futures USD/lb retain separate units and economic identities.

The frozen valuation runners reproduce conditional operating proxies. They do not represent a validated physical corporate valuation. Fixed-current-Q particle fits are in-sample conditional experiments; their optimizer status, resolution and independent seed checks are retained. The historical P-only gold benchmark is distinct and shows interval undercoverage. Copper's available delivery strip does not reconstruct historical spot or front-month futures.

Historical origin experiments recalibrate options on 30 recovered 64-contract surfaces. All four physical models now share 29 targets. Gold RMSE is 66.35/66.77/66.84/65.81 USD/oz for GBM/Heston/Bates/Bates--Hawkes, versus 66.09 for no-change. Jump-model nominal 95% intervals cover 25/29 observations. The small Hawkes RMSE advantage is descriptive; numerical sensitivity and omitted parameter/basis uncertainty remain explicit. See [the completed gold comparison](outputs/physical_measure/20261011-four-model-gold-complete/summary.json). Jump-model 80% intervals under-cover significantly (Bates 17/29, Bates--Hawkes 16/29), and these origin fits predate the GLD carry correction (q = 0).

A [restricted finite-horizon joint-density argument](outputs/research_notes/RESTRICTED-JOINT-DENSITY.md) establishes the measure construction under explicit model and initial-state assumptions. This theoretical result does not validate the empirical fits. The remaining scientific conditions are documented in [the physical forecasting plan](outputs/research_notes/PHYSICAL-FORECAST-PLAN.md). Publication admission still requires the P/Q estimation and validation, the realized-price and FCFF bridges, attributable claims and the terminal economic assumptions. The folder title does not imply those conditions are fulfilled.

## 24 October 2026 corrections

The valuation now runs on the calendar of `src/barrick_unified/valuation_clock.py` through `src/barrick_unified/dated_valuation.py`: only flows after the 2 September 2026 valuation time are valued (the Q1--Q2 2026 actuals are excluded, the 2026Q3 stub contributes 28/92 of its forecast), revenue uses the average daily price within each quarter, flows are discounted at mid-period and `wacc_0` applies to the first year. Gold paths start from the synchronous XAUUSD spot (USD 4,391.32/oz) and use the corrected engines in `src/barrick_unified/gold_paths.py` (full truncation, exact Hawkes intensity integral), validated against COS prices. GLD options are recalibrated with the 0.40% sponsor fee as carry (`src/pricing/gld_carry.py`). The scenario drift is read as a physical expectation with no gold risk premium; a risk-free discounting of the explicit flows is reported beside the WACC result. Per-share values and the market-price comparison are no longer reported, because the equity bridge is still a zero placeholder.

Results (`outputs/paper_audit_20261024/`): median proxies of USD 56.3--59.5 bn across the four engines, inside the numerical range of a single engine (USD 56.2--60.0 bn across path counts and seeds); terminal value about 83% of the mean; explicit flows to 2030 of USD 10.7--11.1 bn; copper adds USD 2.3 bn of explicit flows. The 7 September runs remain in `outputs/paper_audit/` and `outputs/valuation/` as historical evidence; `data/processed/manifests/valuation/AUTHORITATIVE_MULTIMODEL.json` points to the 24 October run.

## Provenance

Frozen source manifests are preserved. `data/processed/manifests/AUTHORITATIVE_CURRENT.json` still names the 26 August LSE run because the 25 August regression fixture pins its bytes; the LSE market-context statistics quoted in both reports (86 Barrick bars, 16.20%) come from run `20260828T070000Z-lse-nss`, whose manifests are in `data/processed/manifests/20260828T070000Z-lse-nss/`. `barrick_unified.layout.migrated_path` resolves their historical locations in the shared tree without editing recorded input hashes. Migration and report-package ledgers are under `data/processed/provenance`. Changes to paths are verified by offline tests, numerical replay and report text comparison; the local originals remain preserved until final delivery is verified.

Development tests (163 offline pytest cases), chat records, graph tooling and local review material are maintained outside this publication tree and are not uploaded; `pyproject.toml` keeps pytest as an optional extra for them. Reproducibility manifests required by the runners are under data/processed/provenance.
