# Graph Report - Complete Valuation  (2026-10-13)

## Corpus Check
- 250 files · ~182,148 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 50 file(s) not represented in the graph (top: .tex 45, .ipynb 5)

## Summary
- 2131 nodes · 4750 edges · 113 communities (93 shown, 20 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 171 edges (avg confidence: 0.92)
- Token usage: unmetered by the host; zero placeholders do not indicate zero cost.

## Community Hubs (Navigation)
- Physical Models and Admission
- Option Pricing and Calibration
- Copper Evidence and Integration
- Copper Evidence and Integration
- Unified Research and Limits
- Physical Models and Admission
- Operating Value Sensitivities
- Unified Research and Limits
- Unified Research and Limits
- Copper Evidence and Integration
- Unified Research and Limits
- Implementation Verification
- Option Pricing and Calibration
- Option Pricing and Calibration
- Implementation Verification
- Operating Value Sensitivities
- Operating Value Sensitivities
- Physical Models and Admission
- Physical Models and Admission
- Unified Research and Limits
- Option Pricing and Calibration
- Implementation Verification
- Physical Models and Admission
- Copper Evidence and Integration
- Unified Research and Limits
- Option Pricing and Calibration
- Research Modules and Interfaces
- Physical Models and Admission
- Research Modules and Interfaces
- Option Pricing and Calibration
- Physical Models and Admission
- Paper Methods and Findings
- Unified Research and Limits
- Implementation Verification
- Pricing and Scenario Measures
- Unified Research and Limits
- Physical Models and Admission
- Option Pricing and Calibration
- Operating Value Sensitivities
- Physical Models and Admission
- Physical Models and Admission
- Research Modules and Interfaces
- Implementation Verification
- Physical Models and Admission
- Implementation Verification
- Paper Methods and Findings
- Paper Methods and Findings
- Unified Research and Limits
- Implementation Verification
- Option Pricing and Calibration
- Option Pricing and Calibration
- Copper Evidence and Integration
- Pricing and Scenario Measures
- Copper Evidence and Integration
- Unified Research and Limits
- Copper Evidence and Integration
- Unified Research and Limits
- Physical Models and Admission
- Physical Models and Admission
- Research Modules and Interfaces
- Paper Methods and Findings
- Copper Evidence and Integration
- Physical Models and Admission
- Implementation Verification
- Implementation Verification
- Physical Models and Admission
- Research Modules and Interfaces
- Operating Value Sensitivities
- Paper Methods and Findings
- Implementation Verification
- Implementation Verification
- Research Modules and Interfaces
- Research Modules and Interfaces
- Physical Models and Admission
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces
- Implementation Verification
- Research Modules and Interfaces
- Copper Evidence and Integration
- Physical Models and Admission
- Paper Methods and Findings
- Unified Research and Limits
- Unified Research and Limits
- Copper Evidence and Integration
- Unified Research and Limits
- Copper Evidence and Integration
- Unified Research and Limits
- Implementation Verification
- Implementation Verification
- Copper Evidence and Integration
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces
- Physical Models and Admission
- Implementation Verification
- Option Pricing and Calibration
- Research Modules and Interfaces
- Research Modules and Interfaces
- Physical Models and Admission
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces

## God Nodes (most connected - your core abstractions)
1. `numpy` - 107 edges
2. `pathlib` - 105 edges
3. `pandas` - 60 edges
4. `hashlib` - 54 edges
5. `Physical measure research interface: 6 October update` - 53 edges
6. `argparse` - 51 edges
7. `ValuationInputs` - 40 edges
8. `UnitArray` - 34 edges
9. `Bates` - 34 edges
10. `Heston` - 33 edges

## Surprising Connections (you probably didn't know these)
- `origin_selected_returns()` --implements--> `408 copper returns selected at origin from two prices of the same delivery`  [EXTRACTED]
  utilities/python/barrick_unified/futures_history.py → outputs/report_unificato/chapters/09-physical-measure.tex
- `physical_filter()` --implements--> `Particle likelihood integrates latent state substeps and aggregates observed daily returns`  [EXTRACTED]
  utilities/python/barrick_unified/physical_filter.py → outputs/report_unificato/chapters/09-physical-measure.tex
- `fit_gbm()` --implements--> `GBM likelihood uses actual calendar gaps and the Ito arithmetic-drift adjustment`  [EXTRACTED]
  utilities/python/barrick_unified/physical_gbm.py → outputs/report_unificato/chapters/09-physical-measure.tex
- `normal_jump_map()` --implements--> `Normal Esscher mark tilt and positive intensity ratio c_I`  [EXTRACTED]
  utilities/python/barrick_unified/physical_measure.py → outputs/report_unificato/chapters/09-physical-measure.tex
- `physical_total_return_drift()` --implements--> `Physical total price drift includes Brownian and jump risk-premium terms`  [EXTRACTED]
  utilities/python/barrick_unified/physical_measure.py → outputs/report_unificato/chapters/09-physical-measure.tex

## Import Cycles
- 1-file cycle: `utilities/python/audit.py -> utilities/python/audit.py`
- 1-file cycle: `utilities/python/barrick_unified/cli.py -> utilities/python/barrick_unified/cli.py`
- 1-file cycle: `utilities/python/barrick_unified/ib_gold_adapter.py -> utilities/python/barrick_unified/ib_gold_adapter.py`
- 1-file cycle: `utilities/python/barrick_unified/ib_gold_calibration.py -> utilities/python/barrick_unified/ib_gold_calibration.py`
- 1-file cycle: `utilities/python/barrick_unified/lse_adapter.py -> utilities/python/barrick_unified/lse_adapter.py`
- 1-file cycle: `utilities/python/barrick_unified/market_data.py -> utilities/python/barrick_unified/market_data.py`
- 1-file cycle: `utilities/python/barrick_unified/multimodel_valuation.py -> utilities/python/barrick_unified/multimodel_valuation.py`
- 1-file cycle: `utilities/python/barrick_unified/physical_filter.py -> utilities/python/barrick_unified/physical_filter.py`
- 1-file cycle: `utilities/python/build_audited_results.py -> utilities/python/build_audited_results.py`
- 1-file cycle: `utilities/python/pricing/fourier_pricing.py -> utilities/python/pricing/fourier_pricing.py`
- 1-file cycle: `utilities/python/pricing/Sampling.py -> utilities/python/pricing/Sampling.py`
- 1-file cycle: `utilities/python/pricing/oos_validation.py -> utilities/python/pricing/oos_validation.py`
- 1-file cycle: `utilities/python/run_all_thesis_figures.py -> utilities/python/run_all_thesis_figures.py`
- 1-file cycle: `utilities/python/run_research_snapshot.py -> utilities/python/run_research_snapshot.py`
- 1-file cycle: `utilities/python/tools/audit_thesis_figure_provenance.py -> utilities/python/tools/audit_thesis_figure_provenance.py`
- 1-file cycle: `utilities/python/tools/build_lse_nss_manifest.py -> utilities/python/tools/build_lse_nss_manifest.py`
- 1-file cycle: `utilities/python/tools/build_team8_oos_r2_figure.py -> utilities/python/tools/build_team8_oos_r2_figure.py`
- 1-file cycle: `utilities/python/tools/calibrate_physical_origin_q.py -> utilities/python/tools/calibrate_physical_origin_q.py`
- 1-file cycle: `utilities/python/tools/check_integrated_marks.py -> utilities/python/tools/check_integrated_marks.py`
- 1-file cycle: `utilities/python/tools/check_origin_warm_start.py -> utilities/python/tools/check_origin_warm_start.py`

## Hyperedges (group relationships)
- **Pricing Q, frozen scenario R and excluded physical P: dated October 5 audit** — evidence_measure_audit_20261005_pricing_q, evidence_measure_audit_20261005_artificial_r, evidence_measure_audit_20261005_unimplemented_p, evidence_measure_audit_20261005_measure_boundary [EXTRACTED 1.00]
- **Nested candidate commodity-price engine family** — outputs_report_paper_sections_03_methodology_black_scholes_gbm, outputs_report_paper_sections_03_methodology_heston, outputs_report_paper_sections_03_methodology_bates_poisson, outputs_report_paper_sections_03_methodology_bates_hawkes [EXTRACTED 1.00]
- **Three-mine attributable copper perimeter** — outputs_report_paper_sections_04b_copper_extension_copper_mine_perimeter, utilities_docs_copper_integration_lumwana, utilities_docs_copper_integration_zaldivar, utilities_docs_copper_integration_jabal_sayid, utilities_docs_copper_integration_attributable_sales [EXTRACTED 1.00]

## Communities (113 total, 20 thin omitted)

### Community 0 - "Physical Models and Admission"
Cohesion: 0.08
Nodes (40): argparse, asyncio, dated_initialization, datetime, fetch_ib_copper_options, fit_physical_candidates, hawkes, ib_insync (+32 more)

### Community 1 - "Option Pricing and Calibration"
Cohesion: 0.08
Nodes (51): matplotlib_dates, scipy_interpolate, scipy_spatial, BnS, Black-Scholes pricing, implied volatility and vega utilities., bs_objective(), bs_objective(), all_calibrations_successful() (+43 more)

### Community 2 - "Copper Evidence and Integration"
Cohesion: 0.07
Nodes (47): _float_array(), probability_value_exceeds_market(), Any, datetime, ndarray, quantile_rows(), Explicitly provisional stochastic Barrick valuation engine. The engine keeps…, Run one vectorized, deterministic-seed provisional valuation. (+39 more)

### Community 3 - "Copper Evidence and Integration"
Cohesion: 0.06
Nodes (51): math, matplotlib_tri, attributable_copper_margin(), Copper-specific quote audit and attributable operating margin. HXE is American.…, Mine-quarter CoS margin, USD million; volumes ALREADY attributable. sales_kt…, black76_implied_vol(), black76_normalized_vega(), black76_price() (+43 more)

### Community 4 - "Unified Research and Limits"
Cohesion: 0.03
Nodes (57): A fundamental exponential representation, Affine Stochastic Models with Stochastic Volatility and Jumps, Application to Risk-Neutral Exercise Probabilities, Bates as a Unified Jump-Volatility Model, Brownian Motion, Brownian Motion and Compound Poisson as Special Cases, C\`adl\`ag Paths and Independent Increments, C\`adl\`ag trajectories (+49 more)

### Community 5 - "Physical Models and Admission"
Cohesion: 0.06
Nodes (44): pytest, scipy_special, scipy_stats, physical_filter(), Experimental likelihood for a restricted, same-underlying P/Q model. Bootstrap…, premia=(eta_price, log(kappa_P/kappa_Q), log(c), mark_shift_in_SD). State…, fit_gbm(), GBMFit (+36 more)

### Community 6 - "Operating Value Sensitivities"
Cohesion: 0.11
Nodes (40): scipy, _array_hash(), _bh_distribution_figure(), _comparison_figure(), _input_entry(), _latex_quantile_table(), multimodel_quantile_rows(), multimodel_summary_rows() (+32 more)

### Community 7 - "Unified Research and Limits"
Cohesion: 0.04
Nodes (47): Bates: Adding Jump Risk, Bates--Hawkes Calibration, Bates--Hawkes Visual Checks, Bates: Independent Jumps, Calibration, and Tail Errors, Bates Calibration, Black--Scholes as the Baseline, Black--Scholes Baseline: Calibration, Errors, and Rejection, Branching Ratio and Stationarity (+39 more)

### Community 8 - "Unified Research and Limits"
Cohesion: 0.04
Nodes (48): Algebraic Properties of OLS and Goodness-of-Fit, ARIMA Models and Differencing, ARMA, Nonstationarity, ARIMA, and Dynamic Correlation Models, ARMA Models, Asymptotic Normality and Large-Sample Inference, Autoregressive Models, Confidence Intervals, Consequences for OLS Inference (+40 more)

### Community 9 - "Copper Evidence and Integration"
Cohesion: 0.07
Nodes (34): types, IBGoldFuturesOptionProvider, IBGoldSnapshotConfig, last_valid_bid_ask(), parse_utc_timestamp(), Any, DataFrame, datetime (+26 more)

### Community 10 - "Unified Research and Limits"
Cohesion: 0.04
Nodes (25): Applied Cross-Asset Evidence, AR, ARMA and ARIMA Diagnostics, ARCH and GARCH Evidence, Asset Selection: Bonds, Stocks, Dollar, Choice of return measure in this study, Correlation and Regression Design, Data and Econometric Framework, Empirical Gold Dynamics: From Linear Models to Conditional Volatility (+17 more)

### Community 11 - "Implementation Verification"
Cohesion: 0.08
Nodes (40): matplotlib_image, matplotlib_pyplot, matplotlib_ticker, platform, build_team4_operating_figures(), _grouped_bars(), _operating_contract(), _process_components() (+32 more)

### Community 12 - "Option Pricing and Calibration"
Cohesion: 0.10
Nodes (23): ABC, GoldPathResult, GoldPriceModel, GoldSimulationContext, ndarray, Common gold-engine contract., A model whose only output is a conditional gold-price layer., FullBatesHawkesGoldModel (+15 more)

### Community 13 - "Option Pricing and Calibration"
Cohesion: 0.10
Nodes (37): curve_without_lookahead(), fit_nss_curve(), interpolate_rates(), load_rate_history(), nss_design_matrix(), nss_fit_for_date(), nss_rates(), NSSFit (+29 more)

### Community 14 - "Implementation Verification"
Cohesion: 0.08
Nodes (27): copy, typing, Class-based compatibility pipeline for CODE-012. The legacy module is used only…, RefactoredBarrickPipeline, Application services for versioned Barrick experiments., Fail-closed interpretation contracts., Class-based, parity-preserving Barrick valuation pipeline. The package is…, CostForecast (+19 more)

### Community 15 - "Operating Value Sensitivities"
Cohesion: 0.12
Nodes (26): dataclasses, Enum, str, Small unit-aware array boundary. NumPy arrays stay the computational…, Unit, UnitArray, ComponentMarginEngine, MarginProjection (+18 more)

### Community 16 - "Operating Value Sensitivities"
Cohesion: 0.10
Nodes (35): ModuleType, _array_hash(), _canonical_hash(), common_input_fingerprints(), GoldModelRun, load_multimodel_inputs(), load_team8_path_module(), Any (+27 more)

### Community 17 - "Physical Models and Admission"
Cohesion: 0.12
Nodes (15): calibration_core, Bates, BatesParameters, CalibrationReport, feller_feasible_population(), Try a feasible previous-origin point; None requests the global fallback. Dates…, Build a Differential Evolution population satisfying Heston Feller., warm_local_fit() (+7 more)

### Community 18 - "Physical Models and Admission"
Cohesion: 0.07
Nodes (23): calibrate_physical_origin_q, hashlib, package_report, shutil, urllib_request, Chronological initialization; guesses never substitute for a current fit., digest(), main() (+15 more)

### Community 19 - "Unified Research and Limits"
Cohesion: 0.06
Nodes (34): Adapted stochastic process, Asset Prices Under the Physical Measure, Basic Properties of Brownian Motion, Brownian Motion, Construction of Brownian Motion, Definition and Fundamental Properties, Density function, expectation, variance, Derivatives (+26 more)

### Community 20 - "Option Pricing and Calibration"
Cohesion: 0.15
Nodes (33): Exception, bates_seed_from_payload(), calibrate_bs(), calibration_frame(), file_sha256(), find_previous_hawkes_result(), hawkes_payload(), hawkes_seed_from_payload() (+25 more)

### Community 21 - "Implementation Verification"
Cohesion: 0.17
Nodes (32): _acf(), _fit_garch(), objective(), _fractional_difference(), _garch_filter(), generate_empirical_figures(), _gph_d(), load_current_panel() (+24 more)

### Community 22 - "Physical Models and Admission"
Cohesion: 0.11
Nodes (29): Hourly bar-end and equity-session-close alignment; no fill of unmatched dates, Expanding-origin basis conversion diagnostic conditions on target GLD, GBM likelihood uses actual calendar gaps and the Ito arithmetic-drift adjustment, Seven available copper deliveries; four earlier requested deliveries unavailable in attempted retrievals, Rotating-delivery copper returns do not identify spot drift, carry or realised selling-price expectations, Next-session physical forecasts: 750 targets, Physical measure research interface: 6 October update, Fixed-current-Q diffusion GBM estimate is in-sample and not used at historical OOS origins (+21 more)

### Community 23 - "Copper Evidence and Integration"
Cohesion: 0.20
Nodes (27): add_parameter_diagnostics(), calibrate_bates_forward(), calibrate_black76(), calibrate_hawkes_forward(), calibrate_heston_forward(), deterministic_strike_holdout(), _feller_population(), load_team8_modules() (+19 more)

### Community 24 - "Unified Research and Limits"
Cohesion: 0.07
Nodes (27): Confidence Intervals, Cost of sales forecast methodology, Data Sources, Definitions of Financial and Process Metrics, Evolution of the Modeling Strategy, Forecast Results, Goodman's Formula, Handoff to the independent price and valuation layers (+19 more)

### Community 25 - "Option Pricing and Calibration"
Cohesion: 0.13
Nodes (16): scipy_integrate, scipy_optimize, time, Bates option pricing and reproducible surface calibration., Exact event-dependent Bates-Hawkes option-pricing engine. The jump intensity is…, MaturitySlice, OptionSurface, Shared contracts for option-surface calibration in the clean Team 8 build. (+8 more)

### Community 26 - "Research Modules and Interfaces"
Cohesion: 0.13
Nodes (22): importlib_metadata, LSEMarketDataProvider, Path, Official London Strategic Edge SDK adapter. The API key is read locally and is…, Atomically write licensed row-level data below a Git-ignored path., Narrow provider owned by the project, backed by the official SDK., read_private_snapshot(), write_private_snapshot() (+14 more)

### Community 27 - "Physical Models and Admission"
Cohesion: 0.13
Nodes (23): Conditional finite-horizon density established for exact family; changed laws need a separate proof, Mark-dependent excitation, state-dependent tilt or changed initial-state law need a separate proof, Correlated Brownian covariance C and norm eta transpose C inverse eta, Exact CIR/nonmark-dependent Hawkes family: constant normal-mark tilt, finite coefficients and deterministic initial states, Executable entropy coefficient bound checks stated conditions, not empirical or discrete-likelihood admission, Conditional theorem: exact restricted P/Q laws equivalent on each fixed finite horizon, Fixed finite-horizon result does not establish uniform integrability as T tends to infinity, Assumptions and density (+15 more)

### Community 28 - "Research Modules and Interfaces"
Cohesion: 0.11
Nodes (13): array_sha256(), ArtifactRecord, Any, ndarray, Central SHA-256 and manifest helpers used by runs and figures., Accumulate and atomically serialize one public run manifest., RunManifestBuilder, Validated domain contracts shared by the refactored layers. (+5 more)

### Community 29 - "Option Pricing and Calibration"
Cohesion: 0.15
Nodes (8): BatesHawkesExact, phi(), cf(), phi(), cf(), cf(), test_hawkes_zero_excitation_equal_bates(), test_hawkes_zero_intensity_is_valid_boundary()

### Community 30 - "Physical Models and Admission"
Cohesion: 0.14
Nodes (19): numpy_polynomial_hermite, Hawkes baseline, initial intensity and excitation scaled together; decay unchanged, Restricted CIR map: kappa_P = kappa_Q - xi eta_v; kappa theta preserved, _finite(), hawkes_map(), normal_jump_map(), NormalJumpMap, physical_total_return_drift() (+11 more)

### Community 31 - "Paper Methods and Findings"
Cohesion: 0.09
Nodes (14): Common stochastic WACC, DCF Driver and Terminal-Value Audit, Growth, ROIC and reinvestment, Terminal closure and sensitivity, A Three-Stage DCF Framework for Mining Valuation, Barrick-specific implementation contract, Discount rate: currency, risk and capital structure, Executable assumption register for the current experiment (+6 more)

### Community 32 - "Unified Research and Limits"
Cohesion: 0.09
Nodes (22): Bretton Woods and the Dollar, Convertibility and Fixed Parities, Equity–market risk and risk sentiment, From the Gold Narrative to the Barrick Valuation Object, Global growth and industrial demand, Gold Across Monetary Regimes and the Debasement Narrative, Gold and Monetary Discipline, Gold and Silver as Financial Assets (+14 more)

### Community 33 - "Implementation Verification"
Cohesion: 0.13
Nodes (16): ArgumentParser, build_parser(), main(), Command-line interface for the unified Barrick project facade., Choose an acquisition adapter; instrument identities stay provider-specific., select_team8_provider(), Run the offline suite without leaving Python or pytest caches., Dispatch to a named, existing runner without duplicating its logic. (+8 more)

### Community 34 - "Pricing and Scenario Measures"
Cohesion: 0.13
Nodes (18): importlib_util, measure_contract(), Option pricing Q and artificial operating-scenario R are distinct laws., couple_by_terminal_scores(), main(), Paired gold-only vs gold+copper conditional operating-value experiment. Run…, Sensitivity copula via whole-path permutation; preserves copper marginals. rho…, simulate_copper() (+10 more)

### Community 35 - "Unified Research and Limits"
Cohesion: 0.09
Nodes (21): Antithetic Variates, Application in Finance: European Option Pricing with Monte Carlo Simulation, Asian Option Pricing, Comparative Numerical Benchmark for Variance Reduction Methods, Control Variates, Definition and Fundamental Principles, Empirical Validation of Generators, Extension to Jump--Diffusion Process (+13 more)

### Community 36 - "Physical Models and Admission"
Cohesion: 0.10
Nodes (18): 29-origin conditional GBM: no RMSE improvement over no-change; 27/29 nominal 95% intervals cover, One-origin Heston pilot: conditional physical forecast executed, no model superiority or DCF admission, Conditional two-stage Q options/P returns estimator is permitted; not joint maximum likelihood, 11 October 2026 — source layout and figure coverage, 7 October: shared infrastructure and restricted joint density, 8 October: matched forecasts and gold-unit conversion, Chronological initialization update, 9 October, Completed Heston panel and remaining jump-model runs (+10 more)

### Community 37 - "Option Pricing and Calibration"
Cohesion: 0.18
Nodes (13): calibrate_bs(), hawkes_payload(), main(), Calibrate BS, Heston, Bates and Full Bates-Hawkes on one daily GLD surface.…, report_payload(), settings(), ExactHawkesCalibration, clip_full_seed() (+5 more)

### Community 38 - "Operating Value Sensitivities"
Cohesion: 0.13
Nodes (12): MonkeyPatch, migrated_path(), Path, Shared infrastructure paths for both report editions., Resolve a frozen artifact path without rewriting its source manifest., Path, _sha256(), test_accepted_v3_artifacts_remain_byte_identical() (+4 more)

### Community 39 - "Physical Models and Admission"
Cohesion: 0.12
Nodes (16): 29 matched origins for all four physical models: Hawkes has a small descriptive RMSE advantage; GLD observations; jump-model nominal 95% coverage is 25/29, 29 matched origins converted to gold USD/oz: Hawkes RMSE 65.81 versus no-change 66.09; jump-model nominal 95% coverage 25/29; basis and parameter uncertainty omitted, Black–Scholes/GBM constant-volatility gold benchmark, Common 8,192-path WACC array across model comparisons, Full Bates--Hawkes: implemented affine engine, Gold-price engines, Methodology, Option-surface calibration and predictive test (+8 more)

### Community 40 - "Physical Models and Admission"
Cohesion: 0.14
Nodes (15): origin_selected_returns(), Origin-selected, same-delivery futures returns for physical diagnostics., Choose delivery using only origin quotes, then score that delivery. The nearest…, main(), Build a local-only, explicit-delivery copper return diagnostic., isolate_legacy_pricing_imports(), fixture(), test_roll_uses_two_prices_of_same_contract() (+7 more)

### Community 41 - "Research Modules and Interfaces"
Cohesion: 0.17
Nodes (15): collections_abc, Series, Provenance-safe market analytics for the Barrick unified research project., compute_market_summary(), log_returns(), Any, DataFrame, Canonical LSE candle boundary and trailing market statistics. All time-series… (+7 more)

### Community 42 - "Implementation Verification"
Cohesion: 0.24
Nodes (16): build_public_outputs(), _correlation_figure(), _display_path(), _market_context_figure(), _option_surface_figure(), Any, DataFrame, Path (+8 more)

### Community 43 - "Physical Models and Admission"
Cohesion: 0.22
Nodes (17): Artificial operating-scenario law R, Cross-delivery F(0,T) curve imposes scenario means, not fixed-future time drift, UNIFICATO/Utilities-Progetto/MEASURE-AUDIT-20261005.md, Zero drift of a fixed-delivery future under the deterministic-rate pricing convention, GLD shape reanchored to realised gold USD/oz without estimated carry or GLD/oz conversion, Esito, Priorita economiche ancora aperte, Verifica delle misure: oro e rame - 5 ottobre 2026 (+9 more)

### Community 44 - "Implementation Verification"
Cohesion: 0.18
Nodes (12): importlib, Aggregate-only audit of the current GLD LSE option surface. The transformation…, build_frozen_online_figure(), build_hawkes_intensity_figure(), main(), prepare_local_dataset(), Path, Rebuild every Team 8 thesis image from code held in this branch. Current… (+4 more)

### Community 45 - "Paper Methods and Findings"
Cohesion: 0.12
Nodes (7): Eight research teams connect theory, econometrics, simulation, operations and discounted margins, Operating-Value Sensitivity for Barrick Mining: controlled gold and copper experiment, Introduction, Research programme and collaboration, Cross-model central tendency, Operating-Proxy Sensitivities, Structural illustration, not model selection

### Community 46 - "Paper Methods and Findings"
Cohesion: 0.15
Nodes (12): Signed perpetuity and five-year no-terminal closures are separate sensitivities, Corporate FCFF, cash/debt and diluted-share bridge remains unreconciled, A positive WACC–growth spread does not justify perpetual mine production, Gold historical OOS uses original fits, separate from audited current calibration, Conditional next-date repricing, Interpretive limitations and validation, Jump-layer interpretation, Operating uncertainty and research priorities (+4 more)

### Community 47 - "Unified Research and Limits"
Cohesion: 0.12
Nodes (8): Bibliography, Discoveries at a Glance, Contribution, falsifiable boundaries and roadmap, From eight autonomous studies to one chain of evidence, From SF Research to the Integrated Barrick Project, Research question, community and valuation object, Historical August market diagnostics, Comparative synthesis of the eight source studies

### Community 48 - "Implementation Verification"
Cohesion: 0.14
Nodes (6): ConditionalBridgePolicy, Any, ndarray, QuarterGrid, Validated mapping from a fine simulation grid to operating quarters., test_domain_boundaries_fail_closed()

### Community 49 - "Option Pricing and Calibration"
Cohesion: 0.15
Nodes (11): audit_thesis_figure_provenance, os, subprocess, execute(), main(), promote(), Regenerate and optionally promote every analytical thesis figure. This is the…, Retry the LSE US10Y endpoint without mixing asynchronous curve dates. Raw… (+3 more)

### Community 50 - "Option Pricing and Calibration"
Cohesion: 0.17
Nodes (13): collections, re, catalog(), main(), Path, Audit every analytical image used by the unified thesis. The audit proves that…, referenced_images(), rel() (+5 more)

### Community 51 - "Copper Evidence and Integration"
Cohesion: 0.21
Nodes (15): Other 21 gold reference dates were not acquired, not declared unavailable, Three producing copper mines with attributable sold volumes, Already attributable sold copper volumes, Copper extension of an originally gold-only operating perimeter, Copper historical extension — October 3 local acquisition, Copper integration, Probability-measure contract - October 5, 2026, Ten-date preliminary copper pilot spanning July 9–September 2, 2026 (+7 more)

### Community 52 - "Pricing and Scenario Measures"
Cohesion: 0.17
Nodes (15): Option calibration under pricing measure Q, Partners' interests must not be deducted again from already attributable flows, CoS includes depreciation and royalties: component margin is not EBITDA or reconciled EBIT, Same-date NSS Treasury par-yield proxy, not a bootstrapped zero curve, GLD non-distributing call exercise convention checked with an 800-step CRR tree, September 2 GLD calibration: 64 actual structured contracts, Eight-mine attributable gold operating subset, Calibration snapshot and measure discipline (+7 more)

### Community 53 - "Copper Evidence and Integration"
Cohesion: 0.22
Nodes (15): oos_validation, american_futures_price(), copper_surface(), invert(), CRR futures tree: risk-neutral forward drift is zero, premium discounted., sha256_file(), main(), main() (+7 more)

### Community 54 - "Unified Research and Limits"
Cohesion: 0.13
Nodes (10): Accounting and economic validation, Controlled design: one changing layer, End-to-end experiment contract, Executable method and result bundle, External validity and information limits, Layered validation, Measure, dates and simulation design, Numerical and simulation robustness (+2 more)

### Community 55 - "Copper Evidence and Integration"
Cohesion: 0.21
Nodes (13): Monte Carlo standard errors measure mean simulation noise only, UNIFICATO paired five-year operating proxy: no terminal value, 600-step constant-volatility American-to-European HXE approximation, Independent commodity paths primary; whole-path rank permutations are dependence sensitivities, Copper margin: kt sales and USD/lb converted to USD millions using 2204.6226218488 lb/t, Q2 copper sales and CoS fixed for 20 quarters, not mine-level production forecasts, Copper Extension: History and Paired Operating Values, Historical surface and exercise treatment (+5 more)

### Community 56 - "Unified Research and Limits"
Cohesion: 0.14
Nodes (3): Chronological loss accumulation, Cross-sectional calibration geometry, Regenerated market-input and return evidence

### Community 57 - "Physical Models and Admission"
Cohesion: 0.19
Nodes (11): Heston refit: optimizer success at 512 particles, 16 substeps and two training seeds; NOT_DCF, Independent 1,024-particle 16/32-substep checks do not show robust likelihood improvement, Particle/substep sensitivity prevents reliable likelihood ranking, Fixed-current-Q Heston, Bates and Hawkes premium fits are exploratory, Richer physical OOS requires origin-available Q calibration and underlying history, diffusion_novikov_horizon(), Sufficient Brownian-density horizon under the constant-coefficient Q CIR.…, main() (+3 more)

### Community 58 - "Physical Models and Admission"
Cohesion: 0.26
Nodes (10): Every option surface and return training window is available by its forecast origin, observed_origin_surface(), Recover dated observed option inputs without importing forecast outputs., Use only that day's market fields in the frozen per-contract OOS table. A day…, main(), Recover historical observed GLD surfaces for new origin-only calibration.…, observations(), test_dense_sampling_requires_enough_quotes_and_expiries() (+2 more)

### Community 59 - "Research Modules and Interfaces"
Cohesion: 0.32
Nodes (12): build_manifest(), _date_span(), fetch_payload(), _fields(), main(), _manifest_entry(), parse_args(), Any (+4 more)

### Community 60 - "Paper Methods and Findings"
Cohesion: 0.17
Nodes (4): Calibration Sample Audit, What the residual maps add, Why structured sampling is retained, Current surface and predictive audit

### Community 61 - "Copper Evidence and Integration"
Cohesion: 0.18
Nodes (11): Affine Bates–Hawkes with exponential self-exciting intensity, Heston stochastic variance, Lumwana consolidated; Zaldívar and Jabal Sayid equity-accounted, Risk-neutral Hawkes self-excitation does not establish physical or causal news clustering, Barrick Annual Report 2025: ownership, reporting and joint arrangements, Barrick Q2 2026 mine statistics: copper table page 8, Fang and Oosterlee (2008): Fourier-COS option pricing, Hawkes (1971): self-exciting point processes (+3 more)

### Community 62 - "Physical Models and Admission"
Cohesion: 0.24
Nodes (10): A fixed-delivery copper future cannot continue beyond expiry as a five-year spot forecast, Forward P paths condition on the same option-estimated origin variance and intensity as Q, PhysicalPaths, Conditional physical paths on the same underlying and initial state as Q. The…, premia=(eta_S, log(kappa_P/kappa_Q), log(c), mark shift in SD). P starts from…, simulate_physical_paths(), test_futures_cannot_be_projected_past_expiry_or_given_spot_carry(), test_gbm_requires_explicit_physical_drift_on_the_same_diffusion() (+2 more)

### Community 63 - "Implementation Verification"
Cohesion: 0.26
Nodes (9): forecast_log_basis(), gld_forecast_to_gold(), Origin-only deterministic GLD/physical-gold basis transformation., Convert conditional means/quantiles with a deterministic fitted ratio.…, Fit log(GLD USD/share / gold USD/oz) using dates <= origin. Target prices are…, main(), Score completed GLD physical forecasts after origin-only gold conversion., test_conversion_units_and_order_are_preserved() (+1 more)

### Community 64 - "Implementation Verification"
Cohesion: 0.32
Nodes (11): BarSchemaError, canonicalise_lse_candles(), ValueError, Raised when provider rows cannot satisfy the canonical bar contract., Normalize LSE daily candles without silently repairing bad rows., rows(), test_canonical_boundary_sorts_and_uses_float64(), test_duplicate_timestamp_is_rejected() (+3 more)

### Community 65 - "Physical Models and Admission"
Cohesion: 0.29
Nodes (9): Matched-origin physical price forecast metrics with explicit support., Compare completed predictions only on identical origin/target pairs. Every…, summarize_matched_origins(), main(), Freeze matched metrics from completed dated physical forecast files., row(), test_common_support_preserves_failed_optimizer_and_excludes_unmatched_dates(), test_future_training_is_rejected() (+1 more)

### Community 66 - "Research Modules and Interfaces"
Cohesion: 0.29
Nodes (3): ProjectLayout, Path, Canonical, named paths used by people and automation.

### Community 67 - "Operating Value Sensitivities"
Cohesion: 0.26
Nodes (10): _date(), discount_dated_cashflows(), future_quarters(), FutureQuarter, Calendar contract for future cash flows, independent of frozen scenario runs.…, Return future quarter intervals [start, end), ACT/365.25 endpoints.…, Discount explicitly timed flows using caller-supplied zero rates. Rates are…, test_discount_clock_uses_actual_payment_time_and_rejects_past_flows() (+2 more)

### Community 68 - "Paper Methods and Findings"
Cohesion: 0.24
Nodes (5): Cost-of-sales block, Current Operating-Model Evidence, Forecast handoff used by the valuation, Production block, Current operating evidence and the forecast handoff

### Community 69 - "Implementation Verification"
Cohesion: 0.24
Nodes (4): FakeClient, test_adapter_validates_catalog_and_fetches_once_per_symbol(), test_market_fetch_uses_stock_catalog_and_options_underlying_catalog(), test_option_input_fetch_is_one_chain_plus_all_tenors()

### Community 70 - "Implementation Verification"
Cohesion: 0.22
Nodes (8): lse_dataset, nss_curve, main(), Path, Build a redistribution-safe current NSS manifest from a private LSE snapshot., sha256(), test_nss_fit_recovers_a_smooth_curve_and_forward_integrals(), test_nss_requires_enough_distinct_tenors()

### Community 71 - "Research Modules and Interfaces"
Cohesion: 0.38
Nodes (9): build_snapshot(), _catalog_matches(), _date_span(), find_local_lse_key(), _json_default(), main(), Any, Resolve Barrick Mining in LSE and cache licensed inputs locally. The script… (+1 more)

### Community 72 - "Research Modules and Interfaces"
Cohesion: 0.25
Nodes (4): find_local_lse_key(), Any, Find the process/user-scoped key without exposing it., Fetch catalog-validated Barrick equities and the GLD option underlying.…

### Community 73 - "Physical Models and Admission"
Cohesion: 0.42
Nodes (8): Finite-horizon entropy bound for the stated continuous-time family. Under…, restricted_joint_entropy_bound(), inputs(), Validate entropy coefficients, exact Poisson reduction and domain guards., test_bound_retains_correlated_brownian_norm_and_rejects_invalid_map(), test_identity_change_has_zero_relative_entropy(), test_marked_poisson_reduces_to_exact_known_relative_entropy(), test_nonstationarity_is_distinct_from_finite_horizon_density()

### Community 74 - "Research Modules and Interfaces"
Cohesion: 0.33
Nodes (8): audit_current_surface(), load_frozen_team8_module(), OptionSurfaceAudit, Any, DataFrame, Path, Return aggregate audit plus an in-memory sampled surface for plotting., _sha256()

### Community 75 - "Research Modules and Interfaces"
Cohesion: 0.47
Nodes (8): csv_comparison(), main(), png_comparison(), Any, Path, Build a deterministic comparison report for the frozen Team 7 offline run. This…, sha256(), text_comparison()

### Community 76 - "Research Modules and Interfaces"
Cohesion: 0.47
Nodes (8): evidence(), main(), Any, Path, Run and record Team 8 G1.4 unit/benchmark parity without market data., run(), sha256(), write_json()

### Community 77 - "Research Modules and Interfaces"
Cohesion: 0.29
Nodes (3): bateshawkesexact, matplotlib, pil

### Community 78 - "Research Modules and Interfaces"
Cohesion: 0.25
Nodes (7): CODE-010 decisions, D1 — Four models change only the gold-price layer, D2 — Conditional GLD/Q shape bridge, not a physical forecast, D3 — Preserve Team 8 numerical engines, D4 — Common WACC random numbers, D5 — Simulation size, D6 — Full Bates--Hawkes selection language

### Community 79 - "Implementation Verification"
Cohesion: 0.25
Nodes (5): _operational_artifacts(), Any, Return a deterministic, read-only handoff summary., Scan once, pruning generated outputs before descending into them., test_artifact_scan_preserves_non_output_findings()

### Community 81 - "Copper Evidence and Integration"
Cohesion: 0.57
Nodes (7): UNIFICATO/Utilities-Progetto/COPPER-TEMPORAL-20261003.md, Copper fixed-origin OOS: July 9 origin on the same six target dates, Copper: storico, modelli e integrazione completata, 480 common model forecasts; rolling persistence 375 and fixed-origin persistence 333, Rolling IV persistence remains unbeaten by all four models, Copper rolling OOS: six chronological admitted origin–target pairs, Origin-only parameters and projected states; target futures/rates condition IV repricing

### Community 82 - "Physical Models and Admission"
Cohesion: 0.38
Nodes (7): Pan (2002): integrated underlying/option evidence and jump-risk premia, Correlated Brownian shift convention dW_Q = dW_P + eta sqrt(v) dt, Normal Esscher mark tilt and positive intensity ratio c_I, Physical total price drift includes Brownian and jump risk-premium terms, Restricted Q-to-P maps with a finite-horizon density proof under stated assumptions, Cross-measure coefficients require the same traded underlying and event support, Zero copper Bates Q jump intensity cannot acquire positive P jump support

### Community 83 - "Paper Methods and Findings"
Cohesion: 0.29
Nodes (6): Cinque passaggi di revisione, Fonti e riproducibilita, OOS: definizioni e tabella unica, Parametri correnti rifiniti (campione del 2 settembre), Stato dei 27 rilievi, Test numerici e contratto operativo

### Community 84 - "Unified Research and Limits"
Cohesion: 0.29
Nodes (6): Barrick Mining Corporation and Valuation Perimeter, Corporate identity and the choice of case study, Financial and structural perimeter, Operating quantities supplied by the source programme, Risk boundary and permitted use, The company perimeter is a model input

### Community 85 - "Unified Research and Limits"
Cohesion: 0.29
Nodes (6): Common notation, units and model interfaces, Data, Provenance and Experimental Design, Data universe and dates, Evaluation design, Provenance and reproducibility, Research boundaries

### Community 88 - "Copper Evidence and Integration"
Cohesion: 0.33
Nodes (5): Evidence contract, Measure audit: gold and copper, Model and temporal validation, Operating mapping and paired evidence, Permitted reading and replay

### Community 89 - "Unified Research and Limits"
Cohesion: 0.33
Nodes (5): Concluding synthesis, Conclusion and Future Research, Future research programme, Present limitations, What the project has completed

### Community 90 - "Implementation Verification"
Cohesion: 0.33
Nodes (4): parametrize, test_hawkes_uses_prior_point_and_falls_back_on_local_failure(), test_warm_calibration_skips_global_search(), forbidden()

### Community 93 - "Research Modules and Interfaces"
Cohesion: 0.40
Nodes (4): Commands, Complete Valuation, Provenance, Reports and scientific interpretation

### Community 94 - "Research Modules and Interfaces"
Cohesion: 0.40
Nodes (4): Boundary and data flow, CODE-010 system map, Components and ownership, Failure surfaces

### Community 95 - "Research Modules and Interfaces"
Cohesion: 0.40
Nodes (4): Frozen evidence, Interpretation boundary, Operational changes, Team 8 refresh - 2 September 2026

### Community 96 - "Physical Models and Admission"
Cohesion: 0.50
Nodes (3): 11 October 2026 — source layout and figure coverage, Governing layout correction — 11 October 2026, Physical forecasting plan

### Community 97 - "Implementation Verification"
Cohesion: 0.50
Nodes (4): manual_curve_frame(), DataFrame, Return a fresh frame so callers cannot mutate the locked constants., test_manual_curve_is_locked_to_approved_input()

## Knowledge Gaps
- **469 isolated node(s):** `Black–Scholes/GBM constant-volatility gold benchmark`, `Barrick Mining research repository, revised October 5, 2026`, `Generated outputs`, `Research programme and collaboration`, `Introduction` (+464 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 944 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ExactHawkesCalibration` connect `Option Pricing and Calibration` to `Option Pricing and Calibration`, `Option Pricing and Calibration`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **Why does `BatesHawkesExact` connect `Option Pricing and Calibration` to `Physical Models and Admission`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **Why does `Bates` connect `Physical Models and Admission` to `Option Pricing and Calibration`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **What connects `Black–Scholes/GBM constant-volatility gold benchmark`, `Barrick Mining research repository, revised October 5, 2026`, `Generated outputs` to the rest of the system?**
  _469 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Physical Models and Admission` be split into smaller, more focused modules?**
  _Cohesion score 0.0763000852514919 - nodes in this community are weakly interconnected._
- **Should `Option Pricing and Calibration` be split into smaller, more focused modules?**
  _Cohesion score 0.08158508158508158 - nodes in this community are weakly interconnected._
- **Should `Copper Evidence and Integration` be split into smaller, more focused modules?**
  _Cohesion score 0.06605222734254992 - nodes in this community are weakly interconnected._
## Scientific and coverage boundary

The graph indexes canonical Python source/tests and the document topology of both reports, with curated semantic evidence for copper, probability measures and physical-model diagnostics. TeX headings, inclusion and publication-image relationships are explicit lexical topology, not a new mathematical audit. Frozen reference code remains distinguishable by its source paths. Licensed observations, local price rows, logs, archives and duplicate builds are excluded. Image nodes declare referenced deduplicated publication assets; no new visual empirical inference is made.

Restricted physical coefficient maps and a training-only historical P GBM baseline are implemented. Fixed-current-Q richer fits remain in-sample, exploratory and numerically unconverged. The exact constant-tilt CIR/nonmark-dependent Hawkes family now has a conditional finite-horizon joint-density proof. This theoretical result does not establish empirical identification, discrete-likelihood convergence, origin-only richer physical OOS, reconciled FCFF or corporate value. The Heston refit remains NOT_DCF despite optimizer success. The frozen R scenario results retain their separate status.

Original repeated endpoint relationship records are retained in extraction.json. Explicit unresolved AST import boundaries are declared as external stubs, not treated as implemented modules. Host semantic token usage is unavailable; zero means unmetered. The dated 20261005/06 snapshots are preserved.

## Dated physical forecast extension

Thirty observed origin surfaces support conditional two-stage recalibration, without current-Q leakage. The single-origin Heston pilot is executed but not model validation; a 29-origin GBM panel has no RMSE advantage over no-change. Joint maximum likelihood is not mandatory; shared option-estimated initial states and omitted uncertainty are explicit. Fixed-delivery expiry and the September valuation stub constrain revenue/DCF integration. The completed 29-origin GBM/Heston comparison and its origin-only gold-basis conversion are indexed. Neither model improves RMSE over no-change. Two Heston optimizer failures remain in the evaluation. Bates and Bates-Hawkes panels are complete and their matched results are indexed below.

## Completed four-family panel, 11 October

Both jump-model jobs completed on 9 October. All four models share 29 physical targets; Hawkes has a small descriptive RMSE advantage, with only 25/29 coverage at nominal 95% for both jump models. Numerical seed sensitivity remains material. Optional analytical normal-mark integration reduces dispersion in a targeted frozen-parameter stress check but does not establish convergence or replace the frozen OOS panel. No corporate valuation is admitted.
