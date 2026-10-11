# Graph Report - Complete Valuation  (2026-10-11)

## Corpus Check
- 319 files · ~246,231 words
- Verdict: corpus is large enough that graph structure adds value.
- All 45 TeX sources are explicitly represented by document topology despite the detector's unsupported extension.

## Summary
- 3293 nodes · 7491 edges · 138 communities (125 shown, 13 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 324 edges (avg confidence: 0.93)
- Token usage: unmetered by the host; zero placeholders do not indicate zero cost.

## Community Hubs (Navigation)
- Physical Models and Admission
- Frozen Research Reference
- Frozen Research Reference
- Implementation Verification
- Copper Evidence and Integration
- Operating Value Sensitivities
- Option Pricing and Calibration
- Unified Research and Limits
- Option Pricing and Calibration
- Implementation Verification
- Option Pricing and Calibration
- Copper Evidence and Integration
- Option Pricing and Calibration
- Option Pricing and Calibration
- Unified Research and Limits
- Implementation Verification
- Unified Research and Limits
- Copper Evidence and Integration
- Physical Models and Admission
- Operating Value Sensitivities
- Frozen Research Reference
- Implementation Verification
- Unified Research and Limits
- Physical Models and Admission
- Option Pricing and Calibration
- Copper Evidence and Integration
- Option Pricing and Calibration
- Option Pricing and Calibration
- Option Pricing and Calibration
- Option Pricing and Calibration
- Physical Models and Admission
- Copper Evidence and Integration
- Option Pricing and Calibration
- Unified Research and Limits
- Option Pricing and Calibration
- Implementation Verification
- Operating Value Sensitivities
- Operating Value Sensitivities
- Option Pricing and Calibration
- Frozen Research Reference
- Frozen Research Reference
- Option Pricing and Calibration
- Frozen Research Reference
- Unified Research and Limits
- Implementation Verification
- Physical Models and Admission
- Physical Models and Admission
- Implementation Verification
- Physical Models and Admission
- Physical Models and Admission
- Physical Models and Admission
- Implementation Verification
- Copper Evidence and Integration
- Paper Methods and Findings
- Unified Research and Limits
- Implementation Verification
- Unified Research and Limits
- Treasury Curves and Clocks
- Implementation Verification
- Frozen Research Reference
- Option Pricing and Calibration
- Frozen Research Reference
- Option Pricing and Calibration
- Frozen Research Reference
- Operating Value Sensitivities
- Physical Models and Admission
- Physical Models and Admission
- Pricing and Scenario Measures
- Unified Research and Limits
- Frozen Research Reference
- Physical Models and Admission
- Paper Methods and Findings
- Option Pricing and Calibration
- Frozen Research Reference
- Copper Evidence and Integration
- Pricing and Scenario Measures
- Option Pricing and Calibration
- Implementation Verification
- Physical Models and Admission
- Paper Methods and Findings
- Unified Research and Limits
- Option Pricing and Calibration
- Frozen Research Reference
- Copper Evidence and Integration
- Unified Research and Limits
- Paper Methods and Findings
- Frozen Research Reference
- Option Pricing and Calibration
- Frozen Research Reference
- Implementation Verification
- Frozen Research Reference
- Paper Methods and Findings
- Copper Evidence and Integration
- Physical Models and Admission
- Research Modules and Interfaces
- Frozen Research Reference
- Paper Methods and Findings
- Research Modules and Interfaces
- Operating Value Sensitivities
- Frozen Research Reference
- Treasury Curves and Clocks
- Frozen Research Reference
- Frozen Research Reference
- Frozen Research Reference
- Physical Models and Admission
- Frozen Research Reference
- Research Modules and Interfaces
- Physical Models and Admission
- Research Modules and Interfaces
- Research Modules and Interfaces
- Copper Evidence and Integration
- Paper Methods and Findings
- Unified Research and Limits
- Unified Research and Limits
- Copper Evidence and Integration
- Unified Research and Limits
- Copper Evidence and Integration
- Physical Models and Admission
- Option Pricing and Calibration
- Research Modules and Interfaces
- Implementation Verification
- Operating Value Sensitivities
- Copper Evidence and Integration
- Unified Research and Limits
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces
- Frozen Research Reference
- Physical Models and Admission
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces
- Research Modules and Interfaces
- Physical Models and Admission

## God Nodes (most connected - your core abstractions)
1. `numpy` - 169 edges
2. `pathlib` - 135 edges
3. `pandas` - 99 edges
4. `argparse` - 66 edges
5. `hashlib` - 58 edges
6. `Bates` - 55 edges
7. `BatesHawkesExact` - 54 edges
8. `Physical measure research interface: 6 October update` - 53 edges
9. `dataclasses` - 43 edges
10. `ValuationInputs` - 40 edges

## Surprising Connections (you probably didn't know these)
- `observed_origin_surface()` --implements--> `Every option surface and return training window is available by its forecast origin`  [EXTRACTED]
  src/barrick_unified/physical_origins.py → utilities/docs/PHYSICAL-FORECAST-PLAN.md
- `origin_selected_returns()` --implements--> `408 copper returns selected at origin from two prices of the same delivery`  [EXTRACTED]
  src/barrick_unified/futures_history.py → outputs/report_unificato/chapters/09-physical-measure.tex
- `physical_filter()` --implements--> `Particle likelihood integrates latent state substeps and aggregates observed daily returns`  [EXTRACTED]
  src/barrick_unified/physical_filter.py → outputs/report_unificato/chapters/09-physical-measure.tex
- `fit_gbm()` --implements--> `GBM likelihood uses actual calendar gaps and the Ito arithmetic-drift adjustment`  [EXTRACTED]
  src/barrick_unified/physical_gbm.py → outputs/report_unificato/chapters/09-physical-measure.tex
- `normal_jump_map()` --implements--> `Normal Esscher mark tilt and positive intensity ratio c_I`  [EXTRACTED]
  src/barrick_unified/physical_measure.py → outputs/report_unificato/chapters/09-physical-measure.tex

## Import Cycles
- 1-file cycle: `src/audit.py -> src/audit.py`
- 1-file cycle: `src/barrick_unified/cli.py -> src/barrick_unified/cli.py`
- 1-file cycle: `src/barrick_unified/ib_gold_adapter.py -> src/barrick_unified/ib_gold_adapter.py`
- 1-file cycle: `src/barrick_unified/ib_gold_calibration.py -> src/barrick_unified/ib_gold_calibration.py`
- 1-file cycle: `src/barrick_unified/lse_adapter.py -> src/barrick_unified/lse_adapter.py`
- 1-file cycle: `src/barrick_unified/market_data.py -> src/barrick_unified/market_data.py`
- 1-file cycle: `src/barrick_unified/multimodel_valuation.py -> src/barrick_unified/multimodel_valuation.py`
- 1-file cycle: `src/barrick_unified/physical_filter.py -> src/barrick_unified/physical_filter.py`
- 1-file cycle: `src/build_audited_results.py -> src/build_audited_results.py`
- 1-file cycle: `src/pricing/fourier_pricing.py -> src/pricing/fourier_pricing.py`
- 1-file cycle: `src/pricing/Sampling.py -> src/pricing/Sampling.py`
- 1-file cycle: `src/pricing/oos_validation.py -> src/pricing/oos_validation.py`
- 1-file cycle: `src/reference/team-7/src/06_stylized_facts.py -> src/reference/team-7/src/06_stylized_facts.py`
- 1-file cycle: `src/reference/team-7/src/06c_arma_mean_models.py -> src/reference/team-7/src/06c_arma_mean_models.py`
- 1-file cycle: `src/reference/team-7/src/07_garch_estimation.py -> src/reference/team-7/src/07_garch_estimation.py`
- 1-file cycle: `src/reference/team-7/src/08_arfima_analysis.py -> src/reference/team-7/src/08_arfima_analysis.py`
- 1-file cycle: `src/reference/team-8-current/src/ibkr_gld_historical_surface.py -> src/reference/team-8-current/src/ibkr_gld_historical_surface.py`
- 1-file cycle: `src/reference/team-8-current/src/make_missing_ibkr_figures.py -> src/reference/team-8-current/src/make_missing_ibkr_figures.py`
- 1-file cycle: `src/reference/team-8/benchmarks/benchmark_pricing.py -> src/reference/team-8/benchmarks/benchmark_pricing.py`
- 1-file cycle: `src/reference/team-8/historical_validation.py -> src/reference/team-8/historical_validation.py`

## Hyperedges (group relationships)
- **Pricing Q, frozen scenario R and excluded physical P: dated October 5 audit** — evidence_measure_audit_20261005_pricing_q, evidence_measure_audit_20261005_artificial_r, evidence_measure_audit_20261005_unimplemented_p, evidence_measure_audit_20261005_measure_boundary [EXTRACTED 1.00]
- **Nested candidate commodity-price engine family** — outputs_report_paper_sections_03_methodology_black_scholes_gbm, outputs_report_paper_sections_03_methodology_heston, outputs_report_paper_sections_03_methodology_bates_poisson, outputs_report_paper_sections_03_methodology_bates_hawkes [EXTRACTED 1.00]
- **Three-mine attributable copper perimeter** — outputs_report_paper_sections_04b_copper_extension_copper_mine_perimeter, utilities_docs_copper_integration_lumwana, utilities_docs_copper_integration_zaldivar, utilities_docs_copper_integration_jabal_sayid, utilities_docs_copper_integration_attributable_sales [EXTRACTED 1.00]

## Communities (138 total, 13 thin omitted)

### Community 0 - "Physical Models and Admission"
Cohesion: 0.04
Nodes (54): argparse, audit_thesis_figure_provenance, calibrate_physical_origin_q, copy, dated_initialization, fit_physical_candidates, hashlib, json (+46 more)

### Community 1 - "Frozen Research Reference"
Cohesion: 0.05
Nodes (70): arch, matplotlib_pyplot, numpy_fft, seaborn, load_raw(), main(), main(), main() (+62 more)

### Community 2 - "Frozen Research Reference"
Cohesion: 0.08
Nodes (72): io, matplotlib_colors, matplotlib_gridspec, matplotlib_ticker, assert_complete_non_oos_set(), build_simulations(), clean_generated_diagnostics(), compute_model_diagnostics() (+64 more)

### Community 3 - "Implementation Verification"
Cohesion: 0.05
Nodes (54): importlib_metadata, find_local_lse_key(), LSEMarketDataProvider, Any, Path, Official London Strategic Edge SDK adapter. The API key is read locally and is…, Atomically write licensed row-level data below a Git-ignored path., Find the process/user-scoped key without exposing it. (+46 more)

### Community 4 - "Copper Evidence and Integration"
Cohesion: 0.06
Nodes (58): american_futures_price(), attributable_copper_margin(), copper_surface(), invert(), Copper-specific quote audit and attributable operating margin. HXE is American.…, CRR futures tree: risk-neutral forward drift is zero, premium discounted., Mine-quarter CoS margin, USD million; volumes ALREADY attributable. sales_kt…, Audit strike monotonicity/convexity and calendar total variance. (+50 more)

### Community 5 - "Operating Value Sensitivities"
Cohesion: 0.10
Nodes (45): scipy, _array_hash(), _bh_distribution_figure(), _comparison_figure(), _input_entry(), _latex_quantile_table(), multimodel_quantile_rows(), multimodel_summary_rows() (+37 more)

### Community 6 - "Option Pricing and Calibration"
Cohesion: 0.05
Nodes (23): Bates, BatesParameters, Bates option pricing and reproducible surface calibration., Exact event-dependent Bates-Hawkes option-pricing engine. The jump intensity is…, CalibrationReport, feller_feasible_population(), MaturitySlice, OptionSurface (+15 more)

### Community 7 - "Unified Research and Limits"
Cohesion: 0.03
Nodes (57): A fundamental exponential representation, Affine Stochastic Models with Stochastic Volatility and Jumps, Application to Risk-Neutral Exercise Probabilities, Bates as a Unified Jump-Volatility Model, Brownian Motion, Brownian Motion and Compound Poisson as Special Cases, C\`adl\`ag Paths and Independent Increments, C\`adl\`ag trajectories (+49 more)

### Community 8 - "Option Pricing and Calibration"
Cohesion: 0.08
Nodes (49): bateshawkesexact, bns, calibration_workflow, fourier_pricing, matplotlib_tri, load_calibration_surface(), normality_statistics(), option_diagnostics() (+41 more)

### Community 9 - "Implementation Verification"
Cohesion: 0.08
Nodes (49): collections_abc, Provenance-safe market analytics for the Barrick unified research project., BarSchemaError, canonicalise_lse_candles(), compute_market_summary(), log_returns(), Any, DataFrame (+41 more)

### Community 10 - "Option Pricing and Calibration"
Cohesion: 0.05
Nodes (42): BatesHawkesExact, Mathematical sanity and limit tests for the exact (event-dependent) Bates-…, The constant-vol Hawkes characteristic function satisfies phi(0) = 1., The Heston-Hawkes characteristic function satisfies phi(0) = 1., With no jumps (lambda0 = lambda_bar = 0) the constant-vol Hawkes price…, With alpha = 0 and lambda0 = lambda_bar the intensity is constant, so the…, For alpha -> 0 the numerically integrated jump transform must converge to the…, phi(-i) = E[S_T] = S0 exp((r - q) T) for the self-exciting model. (+34 more)

### Community 11 - "Copper Evidence and Integration"
Cohesion: 0.06
Nodes (46): historical_validation, itertools, online_validation, sampling, scipy_interpolate, Sampling strategies for the Team 8 GLD implied-volatility surface., Sampling strategies for the Team 8 GLD implied-volatility surface., attach_prevailing_mean() (+38 more)

### Community 12 - "Option Pricing and Calibration"
Cohesion: 0.11
Nodes (44): scipy_spatial, all_calibrations_successful(), build_origin_calibration_set(), build_summary(), calibration_dir(), calibration_successful(), create_coverage_rows(), discover_surfaces() (+36 more)

### Community 13 - "Option Pricing and Calibration"
Cohesion: 0.06
Nodes (31): Bates, OptionSurface, Validated numeric view of a calibration DataFrame grouped by (T, rate)., BatesHawkes, Vega-weighted proxy objective on a validated market surface., Bates proxy using the stationary mean of a Hawkes intensity. This class…, Return the stationary mean intensity, requiring stationarity., Reference scalar proxy price. (+23 more)

### Community 14 - "Unified Research and Limits"
Cohesion: 0.04
Nodes (47): Bates: Adding Jump Risk, Bates--Hawkes Calibration, Bates--Hawkes Visual Checks, Bates: Independent Jumps, Calibration, and Tail Errors, Bates Calibration, Black--Scholes as the Baseline, Black--Scholes Baseline: Calibration, Errors, and Rejection, Branching Ratio and Stationarity (+39 more)

### Community 15 - "Implementation Verification"
Cohesion: 0.07
Nodes (30): dataclasses, Enum, Application services for versioned Barrick experiments., Class-based compatibility pipeline for CODE-012. The legacy module is used only…, RefactoredBarrickPipeline, Validated domain contracts shared by the refactored layers., ConditionalBridgePolicy, Any (+22 more)

### Community 16 - "Unified Research and Limits"
Cohesion: 0.04
Nodes (48): Algebraic Properties of OLS and Goodness-of-Fit, ARIMA Models and Differencing, ARMA, Nonstationarity, ARIMA, and Dynamic Correlation Models, ARMA Models, Asymptotic Normality and Large-Sample Inference, Autoregressive Models, Confidence Intervals, Consequences for OLS Inference (+40 more)

### Community 17 - "Copper Evidence and Integration"
Cohesion: 0.08
Nodes (37): asyncio, fetch_ib_copper_options, ib_insync, logging, run_copper_oos, last_valid_bid_ask(), parse_utc_timestamp(), datetime (+29 more)

### Community 18 - "Physical Models and Admission"
Cohesion: 0.07
Nodes (31): importlib, numpy, pandas, pytest, origin_selected_returns(), Origin-selected, same-delivery futures returns for physical diagnostics., Choose delivery using only origin quotes, then score that delivery. The nearest…, observed_origin_surface() (+23 more)

### Community 19 - "Operating Value Sensitivities"
Cohesion: 0.07
Nodes (24): UnitArray, CostForecast, CostModel, FrozenTeam4CostModel, ndarray, Protocol, Cost models are independent of every gold-price engine., Compatibility adapter for the accepted 20 Team 4 output values. (+16 more)

### Community 20 - "Frozen Research Reference"
Cohesion: 0.10
Nodes (39): bates_seed_from_payload(), bs_objective(), calibrate_bs(), calibration_frame(), file_sha256(), find_previous_hawkes_result(), hawkes_payload(), hawkes_seed_from_payload() (+31 more)

### Community 21 - "Implementation Verification"
Cohesion: 0.08
Nodes (22): _BaseHawkesCalibration, ExponentialHawkesCalibration, objective(), unpack(), HawkesCalibrationResult, Compact, serializable result returned by both Hawkes calibrators., Return the result as a plain dictionary suitable for JSON export., Validation and result helpers shared by univariate Hawkes models. (+14 more)

### Community 22 - "Unified Research and Limits"
Cohesion: 0.04
Nodes (25): Applied Cross-Asset Evidence, AR, ARMA and ARIMA Diagnostics, ARCH and GARCH Evidence, Asset Selection: Bonds, Stocks, Dollar, Choice of return measure in this study, Correlation and Regression Design, Data and Econometric Framework, Empirical Gold Dynamics: From Linear Models to Conditional Volatility (+17 more)

### Community 23 - "Physical Models and Admission"
Cohesion: 0.08
Nodes (43): 29 matched origins for all four physical models: Hawkes has a small descriptive RMSE advantage; GLD observations; jump-model nominal 95% coverage is 25/29, 29 matched origins converted to gold USD/oz: Hawkes RMSE 65.81 versus no-change 66.09; jump-model nominal 95% coverage 25/29; basis and parameter uncertainty omitted, Paper physical-revenue interface, From pricing measure to physical revenues, Pan (2002): integrated underlying/option evidence and jump-risk premia, Hourly bar-end and equity-session-close alignment; no fill of unmatched dates, Expanding-origin basis conversion diagnostic conditions on target GLD, Correlated Brownian shift convention dW_Q = dW_P + eta sqrt(v) dt (+35 more)

### Community 24 - "Option Pricing and Calibration"
Cohesion: 0.06
Nodes (26): Bates option pricing and reproducible surface calibration. The scalar Fourier…, Calibrate with differential evolution followed by constrained SLSQP. The…, BatesHawkesParameters, Stationary-intensity Bates--Hawkes proxy and calibration workflow., Calibrate the proxy with deterministic optional seed and diagnostics., Named, immutable parameter vector for the stationary Hawkes proxy., CalibrationReport, feller_feasible_population() (+18 more)

### Community 25 - "Copper Evidence and Integration"
Cohesion: 0.10
Nodes (38): ModuleType, _array_hash(), _canonical_hash(), common_input_fingerprints(), GoldModelRun, load_multimodel_inputs(), load_team8_path_module(), Any (+30 more)

### Community 26 - "Option Pricing and Calibration"
Cohesion: 0.10
Nodes (37): curve_without_lookahead(), fit_nss_curve(), interpolate_rates(), load_rate_history(), nss_design_matrix(), nss_fit_for_date(), nss_rates(), NSSFit (+29 more)

### Community 27 - "Option Pricing and Calibration"
Cohesion: 0.11
Nodes (23): ABC, GoldPathResult, GoldPriceModel, GoldSimulationContext, ndarray, Common gold-engine contract., A model whose only output is a conditional gold-price layer., FullBatesHawkesGoldModel (+15 more)

### Community 28 - "Option Pricing and Calibration"
Cohesion: 0.15
Nodes (41): matplotlib_dates, all_calibrations_successful(), build_origin_calibration_set(), build_summary(), calibration_dir(), calibration_successful(), create_coverage_rows(), discover_surfaces() (+33 more)

### Community 29 - "Option Pricing and Calibration"
Cohesion: 0.06
Nodes (20): calibration_core, CalibrationReport, Heston, Little-Heston-Trap characteristic function of log(S_T)., Bates, BatesParameters, Reference European-call price via scalar Fourier inversion., Price all strikes for one maturity from one COS transform grid. (+12 more)

### Community 30 - "Physical Models and Admission"
Cohesion: 0.15
Nodes (32): bates, hawkes, heston, oos_validation, add_parameter_diagnostics(), calibrate_bates_forward(), calibrate_black76(), calibrate_hawkes_forward() (+24 more)

### Community 31 - "Copper Evidence and Integration"
Cohesion: 0.06
Nodes (21): math, scipy_integrate, Black-Scholes pricing, implied volatility and vega utilities., Exact (event-dependent) Bates-Hawkes option-pricing engine. This module…, European call via the single-integral Carr-Madan/Lewis inversion. ``charfunc``…, Return ``(call, put)`` via the Gil-Pelaez probabilities P1, P2. This is a…, COS European-call prices for a vector of strikes at one maturity. ``phi_vals``…, carr_madan_call() (+13 more)

### Community 32 - "Option Pricing and Calibration"
Cohesion: 0.10
Nodes (31): path_simulation, Hawkes, _diffusion_shocks(), forward_rates_from_zero_curve(), _hawkes_jump_blocks(), normal_draws(), Deterministic path engines for the publication's Bates-family diagnostics., Heston diffusion with constant-intensity Poisson lognormal jumps. (+23 more)

### Community 33 - "Unified Research and Limits"
Cohesion: 0.06
Nodes (34): Adapted stochastic process, Asset Prices Under the Physical Measure, Basic Properties of Brownian Motion, Brownian Motion, Construction of Brownian Motion, Definition and Fundamental Properties, Density function, expectation, variance, Derivatives (+26 more)

### Community 34 - "Option Pricing and Calibration"
Cohesion: 0.14
Nodes (34): bates_seed_from_payload(), bs_objective(), calibrate_bs(), calibration_frame(), file_sha256(), find_previous_hawkes_result(), hawkes_payload(), hawkes_seed_from_payload() (+26 more)

### Community 35 - "Implementation Verification"
Cohesion: 0.17
Nodes (32): _acf(), _fit_garch(), objective(), _fractional_difference(), _garch_filter(), generate_empirical_figures(), _gph_d(), load_current_panel() (+24 more)

### Community 36 - "Operating Value Sensitivities"
Cohesion: 0.12
Nodes (29): probability_value_exceeds_market(), datetime, quantile_rows(), Explicitly provisional stochastic Barrick valuation engine. The engine keeps…, Run one vectorized, deterministic-seed provisional valuation., Return the publication table at the canonical percentile levels., _distribution_figure(), _latex_quantile_table() (+21 more)

### Community 37 - "Operating Value Sensitivities"
Cohesion: 0.14
Nodes (18): Unit, ComponentMarginEngine, Revenue less modeled cost of sales before accounting reconciliation., BarrickScenarioEngine, Composition root for one gold model and common Team 4/5 layers., DCFProjection, Team 5 FCFF and terminal-value identities., Team5DCFValuator (+10 more)

### Community 38 - "Option Pricing and Calibration"
Cohesion: 0.10
Nodes (21): bateshawkes, scipy_optimize, Bates option pricing and reproducible surface calibration., bs_objective(), calibrate_bs(), hawkes_payload(), main(), Calibrate BS, Heston, Bates and Full Bates-Hawkes on one daily GLD surface.… (+13 more)

### Community 39 - "Frozen Research Reference"
Cohesion: 0.13
Nodes (30): add_bins(), append_attempt(), balanced_surface(), bin_key(), build_contracts(), build_queues(), connect(), coverage_table() (+22 more)

### Community 40 - "Frozen Research Reference"
Cohesion: 0.14
Nodes (29): axis_nodes(), chebyshev_nodes(), exponential_nodes(), gaussian_center_nodes(), get_nearest_market_points(), interpolation_diagnostics(), load_surface(), main() (+21 more)

### Community 41 - "Option Pricing and Calibration"
Cohesion: 0.09
Nodes (9): BatesParameters, phi(), cf(), Exact event-dependent Bates-Hawkes option-pricing engine. The jump intensity is…, adaptive_cos_call_prices(), carr_madan_call(), cos_call_prices_from_values(), gil_pelaez_call_put() (+1 more)

### Community 42 - "Frozen Research Reference"
Cohesion: 0.14
Nodes (26): fetch_lse_calls(), fetch_lse_historical_yields(), fetch_lse_history(), fetch_lse_option_history(), fetch_lse_yields(), _lse_client(), main(), parse_args() (+18 more)

### Community 43 - "Unified Research and Limits"
Cohesion: 0.07
Nodes (27): Confidence Intervals, Cost of sales forecast methodology, Data Sources, Definitions of Financial and Process Metrics, Evolution of the Modeling Strategy, Forecast Results, Goodman's Formula, Handoff to the independent price and valuation layers (+19 more)

### Community 44 - "Implementation Verification"
Cohesion: 0.15
Nodes (25): platform, build_team4_operating_figures(), _grouped_bars(), _operating_contract(), _process_components(), Any, Figure, Path (+17 more)

### Community 45 - "Physical Models and Admission"
Cohesion: 0.12
Nodes (24): scipy_special, physical_filter(), Experimental likelihood for a restricted, same-underlying P/Q model. Bootstrap…, premia=(eta_price, log(kappa_P/kappa_Q), log(c), mark_shift_in_SD). State…, main(), main(), load_training(), main() (+16 more)

### Community 46 - "Physical Models and Admission"
Cohesion: 0.10
Nodes (21): ExactHawkesCalibration, clip_full_seed(), conditional_objective(), local_minimize(), retain_candidates(), Calibrate the exact Heston-Hawkes model. When ``hawkes_seed`` is supplied, it…, Calibration API for the exact affine Heston-Hawkes pricer., The calibration objective must reject non-stationary alpha >= beta. (+13 more)

### Community 47 - "Implementation Verification"
Cohesion: 0.13
Nodes (25): lse_dataset, build_calibration_sample(), interpolate_zero_rates(), normalise_lse_chain(), normalise_lse_history(), normalise_lse_yield_curve(), normalise_lse_yield_history(), _numeric() (+17 more)

### Community 48 - "Physical Models and Admission"
Cohesion: 0.13
Nodes (21): numpy_polynomial_hermite, Hawkes baseline, initial intensity and excitation scaled together; decay unchanged, diffusion_novikov_horizon(), _finite(), hawkes_map(), normal_jump_map(), NormalJumpMap, physical_total_return_drift() (+13 more)

### Community 49 - "Physical Models and Admission"
Cohesion: 0.13
Nodes (22): Conditional finite-horizon density established for exact family; changed laws need a separate proof, main(), Mark-dependent excitation, state-dependent tilt or changed initial-state law need a separate proof, Correlated Brownian covariance C and norm eta transpose C inverse eta, Exact CIR/nonmark-dependent Hawkes family: constant normal-mark tilt, finite coefficients and deterministic initial states, Executable entropy coefficient bound checks stated conditions, not empirical or discrete-likelihood admission, Conditional theorem: exact restricted P/Q laws equivalent on each fixed finite horizon, Fixed finite-horizon result does not establish uniform integrability as T tends to infinity (+14 more)

### Community 50 - "Physical Models and Admission"
Cohesion: 0.14
Nodes (18): forecast_log_basis(), gld_forecast_to_gold(), Origin-only deterministic GLD/physical-gold basis transformation., Convert conditional means/quantiles with a deterministic fitted ratio.…, Fit log(GLD USD/share / gold USD/oz) using dates <= origin. Target prices are…, Matched-origin physical price forecast metrics with explicit support., Compare completed predictions only on identical origin/target pairs. Every…, summarize_matched_origins() (+10 more)

### Community 51 - "Implementation Verification"
Cohesion: 0.14
Nodes (17): IBGoldFuturesOptionProvider, IBGoldSnapshotConfig, Any, DataFrame, Path, Read-only historical collector for standard COMEX Gold options., Request independent contracts concurrently in pacing-safe chunks., Select distinct standard COMEX ``OG`` expiries after ``snapshot``. (+9 more)

### Community 52 - "Copper Evidence and Integration"
Cohesion: 0.19
Nodes (23): growth_path(), main(), ModelParams, percentile_summary(), plot_base(), plot_scenarios(), ndarray, Path (+15 more)

### Community 53 - "Paper Methods and Findings"
Cohesion: 0.09
Nodes (14): Common stochastic WACC, DCF Driver and Terminal-Value Audit, Growth, ROIC and reinvestment, Terminal closure and sensitivity, A Three-Stage DCF Framework for Mining Valuation, Barrick-specific implementation contract, Discount rate: currency, risk and capital structure, Executable assumption register for the current experiment (+6 more)

### Community 54 - "Unified Research and Limits"
Cohesion: 0.09
Nodes (22): Bretton Woods and the Dollar, Convertibility and Fixed Parities, Equity–market risk and risk sentiment, From the Gold Narrative to the Barrick Valuation Object, Global growth and industrial demand, Gold Across Monetary Regimes and the Debasement Narrative, Gold and Monetary Discipline, Gold and Silver as Financial Assets (+14 more)

### Community 55 - "Implementation Verification"
Cohesion: 0.13
Nodes (16): ArgumentParser, build_parser(), main(), Command-line interface for the unified Barrick project facade., Choose an acquisition adapter; instrument identities stay provider-specific., select_team8_provider(), Run the offline suite without leaving Python or pytest caches., Dispatch to a named, existing runner without duplicating its logic. (+8 more)

### Community 56 - "Unified Research and Limits"
Cohesion: 0.09
Nodes (21): Antithetic Variates, Application in Finance: European Option Pricing with Monte Carlo Simulation, Asian Option Pricing, Comparative Numerical Benchmark for Variance Reduction Methods, Control Variates, Definition and Fundamental Principles, Empirical Validation of Generators, Extension to Jump--Diffusion Process (+13 more)

### Community 57 - "Treasury Curves and Clocks"
Cohesion: 0.16
Nodes (17): fit_nss_curve(), interpolate_rates(), nss_design_matrix(), nss_rates(), NSSFit, _phi1(), ndarray, No-look-ahead Treasury curve utilities using Nelson-Siegel-Svensson (NSS). Team… (+9 more)

### Community 58 - "Implementation Verification"
Cohesion: 0.15
Nodes (21): _chain_signature(), _feller_constraint(), _forecast_iv(), _forecast_parameters(), _initial_calibration(), _normalized_grid(), parameter_names(), parameter_stability() (+13 more)

### Community 59 - "Frozen Research Reference"
Cohesion: 0.14
Nodes (17): package_report, shutil, build_frozen_online_figure(), build_hawkes_intensity_figure(), main(), prepare_local_dataset(), Path, Rebuild every Team 8 thesis image from code held in this branch. Current… (+9 more)

### Community 60 - "Option Pricing and Calibration"
Cohesion: 0.14
Nodes (19): scipy_stats, compare_asian_pricing(), ensure_output_folders(), main(), plot_call_convergence(), Generate compact reproducibility outputs for the Monte Carlo risk article., write_summary(), black_scholes_call() (+11 more)

### Community 61 - "Frozen Research Reference"
Cohesion: 0.14
Nodes (18): run_variance_reduction(), antithetic_variates(), AntitheticResult, control_variate_single(), control_variates_multi(), ControlVariateResult, importance_sampling_normal_shift(), ImportanceSamplingResult (+10 more)

### Community 62 - "Option Pricing and Calibration"
Cohesion: 0.11
Nodes (3): BatesHawkesExact, phi(), cf()

### Community 63 - "Frozen Research Reference"
Cohesion: 0.15
Nodes (19): plot_lcg_diagnostics(), box_muller_from_uniforms(), chi_square_uniform_test(), empirical_correlation(), inverse_exponential(), lcg_uniform(), ndarray, qq_data_standard_normal() (+11 more)

### Community 64 - "Operating Value Sensitivities"
Cohesion: 0.13
Nodes (12): MonkeyPatch, migrated_path(), Path, Shared infrastructure paths for both report editions., Resolve a frozen artifact path without rewriting its source manifest., Path, _sha256(), small_config() (+4 more)

### Community 65 - "Physical Models and Admission"
Cohesion: 0.12
Nodes (16): 29-origin conditional GBM: no RMSE improvement over no-change; 27/29 nominal 95% intervals cover, One-origin Heston pilot: conditional physical forecast executed, no model superiority or DCF admission, Conditional two-stage Q options/P returns estimator is permitted; not joint maximum likelihood, 7 October: shared infrastructure and restricted joint density, 8 October: matched forecasts and gold-unit conversion, Chronological initialization update, 9 October, Completed Heston panel and remaining jump-model runs, Historical origin experiment and forward paths (+8 more)

### Community 66 - "Physical Models and Admission"
Cohesion: 0.19
Nodes (13): fit_gbm(), GBMFit, predictive_log_score(), Exact irregular-time GBM likelihood, with explicit physical drift. Historical-…, main(), Estimate a dated GLD P-drift diagnostic; no corporate valuation output., main(), Exact conditional GBM P forecasts with a freshly fitted Q sigma per origin. (+5 more)

### Community 67 - "Pricing and Scenario Measures"
Cohesion: 0.15
Nodes (14): importlib_util, measure_contract(), Option pricing Q and artificial operating-scenario R are distinct laws., Paired gold-only vs gold+copper conditional operating-value experiment. Run…, load_generator(), main(), Path, Regenerate the synthetic Team 5 DCF figure inside the unified branch. The… (+6 more)

### Community 68 - "Unified Research and Limits"
Cohesion: 0.11
Nodes (9): Bibliography, Discoveries at a Glance, Historical August market diagnostics, Comparative synthesis of the eight source studies, Concluding synthesis, Conclusion and Future Research, Future research programme, Present limitations (+1 more)

### Community 69 - "Frozen Research Reference"
Cohesion: 0.14
Nodes (9): aggregate(), discover_surfaces(), evaluate_date(), load_surface(), main(), OFFLINE-ONLY cross-date sampling audit. This script NEVER connects to IBKR. By…, Reconstruct IV via normalized thin-plate RBF. Returns: - all-surface…, Structured 2-D market-point sampling. Supported 8x8 strategies: UU = Uniform T,… (+1 more)

### Community 70 - "Physical Models and Admission"
Cohesion: 0.22
Nodes (17): Artificial operating-scenario law R, Cross-delivery F(0,T) curve imposes scenario means, not fixed-future time drift, UNIFICATO/Utilities-Progetto/MEASURE-AUDIT-20261005.md, Zero drift of a fixed-delivery future under the deterministic-rate pricing convention, GLD shape reanchored to realised gold USD/oz without estimated carry or GLD/oz conversion, Esito, Priorita economiche ancora aperte, Verifica delle misure: oro e rame - 5 ottobre 2026 (+9 more)

### Community 71 - "Paper Methods and Findings"
Cohesion: 0.12
Nodes (7): Eight research teams connect theory, econometrics, simulation, operations and discounted margins, Operating-Value Sensitivity for Barrick Mining: controlled gold and copper experiment, Introduction, Research programme and collaboration, Cross-model central tendency, Operating-Proxy Sensitivities, Structural illustration, not model selection

### Community 72 - "Option Pricing and Calibration"
Cohesion: 0.18
Nodes (15): Reusable Monte Carlo utilities for the Starting Finance Club PoliTo article., black_scholes_put(), Return the Black-Scholes price of a European put., ndarray, Stochastic process simulators used in the article examples., Simulate a Merton jump-diffusion path by drawing explicit jump times., Simulate one exact geometric Brownian motion path on a time grid., Simulate correlated geometric Brownian motion paths. (+7 more)

### Community 73 - "Frozen Research Reference"
Cohesion: 0.16
Nodes (9): ExactHawkesCalibration, conditional_objective(), Option-surface calibration for the exact affine Bates-Hawkes pricer. The…, Vega-weighted objective for exact Hawkes with constant volatility., Calibrate the constant-volatility exact Hawkes option model., Map the eleven optimizer variables to named model parameters., Return a nearby diffusion seed satisfying the Heston Feller condition., Vega-weighted objective for the full affine Heston-Hawkes model. (+1 more)

### Community 74 - "Copper Evidence and Integration"
Cohesion: 0.21
Nodes (15): Other 21 gold reference dates were not acquired, not declared unavailable, Three producing copper mines with attributable sold volumes, Already attributable sold copper volumes, Copper extension of an originally gold-only operating perimeter, Copper historical extension — October 3 local acquisition, Copper integration, Probability-measure contract - October 5, 2026, Ten-date preliminary copper pilot spanning July 9–September 2, 2026 (+7 more)

### Community 75 - "Pricing and Scenario Measures"
Cohesion: 0.17
Nodes (15): Option calibration under pricing measure Q, Partners' interests must not be deducted again from already attributable flows, CoS includes depreciation and royalties: component margin is not EBITDA or reconciled EBIT, Same-date NSS Treasury par-yield proxy, not a bootstrapped zero curve, GLD non-distributing call exercise convention checked with an 800-step CRR tree, September 2 GLD calibration: 64 actual structured contracts, Eight-mine attributable gold operating subset, Calibration snapshot and measure discipline (+7 more)

### Community 76 - "Option Pricing and Calibration"
Cohesion: 0.17
Nodes (10): BnS, Black-Scholes pricing, implied volatility and vega utilities., bs_objective(), calibrate_bs(), hawkes_payload(), main(), Calibrate BS, Heston, Bates and Full Bates-Hawkes on one daily GLD surface.…, report_payload() (+2 more)

### Community 77 - "Implementation Verification"
Cohesion: 0.22
Nodes (14): _factor(), fit_nss_curve(), residual(), nss_zero_rates(), NSSFit, ndarray, quarterly_forward_rates(), Deterministic Nelson--Siegel--Svensson fitting for the LSE Treasury curve. The… (+6 more)

### Community 78 - "Physical Models and Admission"
Cohesion: 0.21
Nodes (12): datetime, CLI for the conditional four-model Barrick valuation experiment., Read-only underlying-history acquisition; local licensed data, no orders. Daily…, build_snapshot(), _catalog_matches(), _date_span(), find_local_lse_key(), _json_default() (+4 more)

### Community 79 - "Paper Methods and Findings"
Cohesion: 0.15
Nodes (10): Corporate FCFF, cash/debt and diluted-share bridge remains unreconciled, Gold historical OOS uses original fits, separate from audited current calibration, Conditional next-date repricing, Interpretive limitations and validation, Jump-layer interpretation, Operating uncertainty and research priorities, Out-of-Sample Evidence and Model Risk, Reproducibility, numerical accuracy and economic validity are distinct (+2 more)

### Community 80 - "Unified Research and Limits"
Cohesion: 0.13
Nodes (10): Accounting and economic validation, Controlled design: one changing layer, End-to-end experiment contract, Executable method and result bundle, External validity and information limits, Layered validation, Measure, dates and simulation design, Numerical and simulation robustness (+2 more)

### Community 81 - "Option Pricing and Calibration"
Cohesion: 0.13
Nodes (6): cf(), Price a European call under the constant-vol exact-Hawkes model., Price a European call under the Heston-Hawkes exact model., Constant-vol exact-Hawkes call via Gil-Pelaez (cross-check)., Constant-vol exact-Hawkes European put via Gil-Pelaez., Heston-Hawkes exact European put via Gil-Pelaez.

### Community 82 - "Frozen Research Reference"
Cohesion: 0.21
Nodes (10): BnS, build_all_historical_surfaces(), build_calibration_surface(), _eligible_surface_from_panel(), load_option_panel(), main(), _normalise_panel(), Offline builders for historical GLD option surfaces. This module never connects… (+2 more)

### Community 83 - "Copper Evidence and Integration"
Cohesion: 0.21
Nodes (13): Monte Carlo standard errors measure mean simulation noise only, UNIFICATO paired five-year operating proxy: no terminal value, 600-step constant-volatility American-to-European HXE approximation, Independent commodity paths primary; whole-path rank permutations are dependence sensitivities, Copper margin: kt sales and USD/lb converted to USD millions using 2204.6226218488 lb/t, Q2 copper sales and CoS fixed for 20 quarters, not mine-level production forecasts, Copper Extension: History and Paired Operating Values, Historical surface and exercise treatment (+5 more)

### Community 84 - "Unified Research and Limits"
Cohesion: 0.14
Nodes (3): Chronological loss accumulation, Cross-sectional calibration geometry, Regenerated market-input and return evidence

### Community 85 - "Paper Methods and Findings"
Cohesion: 0.20
Nodes (13): Black–Scholes/GBM constant-volatility gold benchmark, Common 8,192-path WACC array across model comparisons, Full Bates--Hawkes: implemented affine engine, Gold-price engines, Methodology, Option-surface calibration and predictive test, Team 4 cost and production models, Valuation mapping (+5 more)

### Community 86 - "Frozen Research Reference"
Cohesion: 0.24
Nodes (13): run_return_risk_examples(), conditional_value_at_risk(), empirical_inverse_cdf(), ndarray, Return simulation and portfolio risk helpers., Simulate returns from a finite mixture of normal distributions., Map uniforms to a return sample through the empirical inverse CDF., Return the lower-tail empirical Value-at-Risk at level alpha. (+5 more)

### Community 87 - "Option Pricing and Calibration"
Cohesion: 0.17
Nodes (7): csv, re, Handoff-friendly orchestration for the unified Barrick research project.…, test_handoff_status_is_ready(), Check shared entry points and standalone report delivery boundaries., test_every_registered_stage_exists_in_shared_source_tree(), zipfile

### Community 88 - "Frozen Research Reference"
Cohesion: 0.29
Nodes (12): DatetimeIndex, discover_surface_files(), inspect_surface(), load_trading_dates(), main(), DataFrame, Path, Timestamp (+4 more)

### Community 89 - "Implementation Verification"
Cohesion: 0.18
Nodes (12): matplotlib_image, build_figure(), load_validated_metrics(), main(), parse_args(), Namespace, Path, Render the two-benchmark OOS R-squared comparison as a PNG. (+4 more)

### Community 90 - "Frozen Research Reference"
Cohesion: 0.15
Nodes (7): Find the closest real market options given a theoretical (T, K) grid., Extract options based on a uniformly spaced (T, K) grid., Calculate N Chebyshev nodes rescaled to the interval [a, b]., Extract options based on Chebyshev nodes (denser at boundaries)., Reconstructs the surface using the sampled points and calculates the error…, Provides methods for sampling option data points from a full dataset based on…, Sampling

### Community 91 - "Paper Methods and Findings"
Cohesion: 0.17
Nodes (4): Calibration Sample Audit, What the residual maps add, Why structured sampling is retained, Current surface and predictive audit

### Community 92 - "Copper Evidence and Integration"
Cohesion: 0.18
Nodes (11): Affine Bates–Hawkes with exponential self-exciting intensity, Heston stochastic variance, Lumwana consolidated; Zaldívar and Jabal Sayid equity-accounted, Risk-neutral Hawkes self-excitation does not establish physical or causal news clustering, Barrick Annual Report 2025: ownership, reporting and joint arrangements, Barrick Q2 2026 mine statistics: copper table page 8, Fang and Oosterlee (2008): Fourier-COS option pricing, Hawkes (1971): self-exciting point processes (+3 more)

### Community 93 - "Physical Models and Admission"
Cohesion: 0.24
Nodes (10): PhysicalPaths, Conditional physical paths on the same underlying and initial state as Q. The…, premia=(eta_S, log(kappa_P/kappa_Q), log(c), mark shift in SD). P starts from…, simulate_physical_paths(), A fixed-delivery copper future cannot continue beyond expiry as a five-year spot forecast, Forward P paths condition on the same option-estimated origin variance and intensity as Q, test_futures_cannot_be_projected_past_expiry_or_given_spot_carry(), test_gbm_requires_explicit_physical_drift_on_the_same_diffusion() (+2 more)

### Community 94 - "Research Modules and Interfaces"
Cohesion: 0.29
Nodes (3): ProjectLayout, Path, Canonical, named paths used by people and automation.

### Community 95 - "Frozen Research Reference"
Cohesion: 0.33
Nodes (11): choose_contract_grid(), chunks(), connect(), evenly_spaced_actual_strikes(), finite_positive(), get_chain(), get_current_spot(), main() (+3 more)

### Community 96 - "Paper Methods and Findings"
Cohesion: 0.24
Nodes (5): Cost-of-sales block, Current Operating-Model Evidence, Forecast handoff used by the valuation, Production block, Current operating evidence and the forecast handoff

### Community 97 - "Research Modules and Interfaces"
Cohesion: 0.20
Nodes (3): ndarray, QuarterGrid, Validated mapping from a fine simulation grid to operating quarters.

### Community 98 - "Operating Value Sensitivities"
Cohesion: 0.24
Nodes (10): _date(), discount_dated_cashflows(), future_quarters(), FutureQuarter, Calendar contract for future cash flows, independent of frozen scenario runs.…, Return future quarter intervals [start, end), ACT/365.25 endpoints.…, Discount explicitly timed flows using caller-supplied zero rates. Rates are…, test_discount_clock_uses_actual_payment_time_and_rejects_past_flows() (+2 more)

### Community 99 - "Frozen Research Reference"
Cohesion: 0.18
Nodes (6): BnS, Calculates the Black-Scholes Vega. S: Spot Price K: Strike Price T: Time to…, Cumulative distribution function for the standard normal distribution., Calculate the Black-Scholes price of a European Call option. ### Parameters: S:…, Calculate Implied Volatility using the Bisection method. ### Parameters: price:…, Black-Scholes European Call Option pricing and implied volatility calculator.…

### Community 100 - "Treasury Curves and Clocks"
Cohesion: 0.29
Nodes (11): curve_without_lookahead(), load_rate_history(), nss_fit_for_date(), DataFrame, Path, Timestamp, rates_for_date(), Return the latest Treasury cross-section with curve_date <= observation_date. (+3 more)

### Community 101 - "Frozen Research Reference"
Cohesion: 0.40
Nodes (9): main(), plot_jump_paths(), plot_variance_paths(), ndarray, Path, Generate synthetic figures for the Beyond Black-Scholes theory article., simulate_jump_paths(), simulate_variance_paths() (+1 more)

### Community 102 - "Frozen Research Reference"
Cohesion: 0.44
Nodes (9): _get_spot(), main(), _normalise_raw(), DataFrame, Path, Timestamp, Rebuild an existing IBKR full GLD surface with NSS Treasury rates OFFLINE. This…, _read_csv() (+1 more)

### Community 103 - "Frozen Research Reference"
Cohesion: 0.36
Nodes (8): collections, catalog(), main(), Path, Audit every analytical image used by the unified thesis. The audit proves that…, referenced_images(), rel(), sha256()

### Community 104 - "Physical Models and Admission"
Cohesion: 0.42
Nodes (8): Finite-horizon entropy bound for the stated continuous-time family. Under…, restricted_joint_entropy_bound(), inputs(), Validate entropy coefficients, exact Poisson reduction and domain guards., test_bound_retains_correlated_brownian_norm_and_rejects_invalid_map(), test_identity_change_has_zero_relative_entropy(), test_marked_poisson_reduces_to_exact_known_relative_entropy(), test_nonstationarity_is_distinct_from_finite_horizon_density()

### Community 105 - "Frozen Research Reference"
Cohesion: 0.56
Nodes (8): _correlated_normals(), _inputs(), ndarray, Team 8 2026-09-02 path adapter for the unified Barrick experiment. The…, simulate_bates_paths(), simulate_full_hawkes_paths(), simulate_gbm_paths(), simulate_heston_paths()

### Community 106 - "Research Modules and Interfaces"
Cohesion: 0.47
Nodes (8): csv_comparison(), main(), png_comparison(), Any, Path, Build a deterministic comparison report for the frozen Team 7 offline run. This…, sha256(), text_comparison()

### Community 107 - "Physical Models and Admission"
Cohesion: 0.29
Nodes (7): Heston refit: optimizer success at 512 particles, 16 substeps and two training seeds; NOT_DCF, Independent 1,024-particle 16/32-substep checks do not show robust likelihood improvement, Particle/substep sensitivity prevents reliable likelihood ranking, Fixed-current-Q Heston, Bates and Hawkes premium fits are exploratory, Richer physical OOS requires origin-available Q calibration and underlying history, Gaussian limit, coefficient-map and jump-support checks are implementation evidence, Particle likelihood integrates latent state substeps and aggregates observed daily returns

### Community 108 - "Research Modules and Interfaces"
Cohesion: 0.36
Nodes (3): Any, Accumulate and atomically serialize one public run manifest., RunManifestBuilder

### Community 109 - "Research Modules and Interfaces"
Cohesion: 0.25
Nodes (7): CODE-010 decisions, D1 — Four models change only the gold-price layer, D2 — Conditional GLD/Q shape bridge, not a physical forecast, D3 — Preserve Team 8 numerical engines, D4 — Common WACC random numbers, D5 — Simulation size, D6 — Full Bates--Hawkes selection language

### Community 110 - "Copper Evidence and Integration"
Cohesion: 0.57
Nodes (7): UNIFICATO/Utilities-Progetto/COPPER-TEMPORAL-20261003.md, Copper fixed-origin OOS: July 9 origin on the same six target dates, Copper: storico, modelli e integrazione completata, 480 common model forecasts; rolling persistence 375 and fixed-origin persistence 333, Rolling IV persistence remains unbeaten by all four models, Copper rolling OOS: six chronological admitted origin–target pairs, Origin-only parameters and projected states; target futures/rates condition IV repricing

### Community 111 - "Paper Methods and Findings"
Cohesion: 0.29
Nodes (6): Cinque passaggi di revisione, Fonti e riproducibilita, OOS: definizioni e tabella unica, Parametri correnti rifiniti (campione del 2 settembre), Stato dei 27 rilievi, Test numerici e contratto operativo

### Community 112 - "Unified Research and Limits"
Cohesion: 0.29
Nodes (6): Barrick Mining Corporation and Valuation Perimeter, Corporate identity and the choice of case study, Financial and structural perimeter, Operating quantities supplied by the source programme, Risk boundary and permitted use, The company perimeter is a model input

### Community 113 - "Unified Research and Limits"
Cohesion: 0.29
Nodes (6): Common notation, units and model interfaces, Data, Provenance and Experimental Design, Data universe and dates, Evaluation design, Provenance and reproducibility, Research boundaries

### Community 114 - "Copper Evidence and Integration"
Cohesion: 0.29
Nodes (3): code(), Deterministically rebuild the modifiable Bates/Hawkes notebooks., main()

### Community 116 - "Copper Evidence and Integration"
Cohesion: 0.33
Nodes (5): Evidence contract, Measure audit: gold and copper, Model and temporal validation, Operating mapping and paired evidence, Permitted reading and replay

### Community 117 - "Physical Models and Admission"
Cohesion: 0.40
Nodes (6): previous_fit(), Latest successful strictly earlier artifact in this experiment only., main(), main(), expand(), objective()

### Community 118 - "Option Pricing and Calibration"
Cohesion: 0.33
Nodes (3): phi(), Constant-vol exact-Hawkes call prices for a vector of strikes (COS). Returns a…, Heston--Hawkes call prices for a vector of strikes using COS. This is the full…

### Community 119 - "Research Modules and Interfaces"
Cohesion: 0.40
Nodes (4): main(), Path, Independent acceptance checks for the Team 7 G1.3 evidence package., sha256()

### Community 120 - "Implementation Verification"
Cohesion: 0.33
Nodes (4): parametrize, test_hawkes_uses_prior_point_and_falls_back_on_local_failure(), test_warm_calibration_skips_global_search(), forbidden()

### Community 121 - "Operating Value Sensitivities"
Cohesion: 0.53
Nodes (4): _inputs(), test_growth_roic_and_reinvestment_schedule_matches_config(), test_terminal_multiple_moves_in_expected_directions(), test_zero_shock_wacc_follows_actual_mean_reversion_and_floor()

### Community 123 - "Unified Research and Limits"
Cohesion: 0.40
Nodes (4): Contribution, falsifiable boundaries and roadmap, From eight autonomous studies to one chain of evidence, From SF Research to the Integrated Barrick Project, Research question, community and valuation object

### Community 124 - "Research Modules and Interfaces"
Cohesion: 0.40
Nodes (4): Commands, Complete Valuation, Provenance, Reports and scientific interpretation

### Community 125 - "Research Modules and Interfaces"
Cohesion: 0.40
Nodes (4): Boundary and data flow, CODE-010 system map, Components and ownership, Failure surfaces

### Community 126 - "Research Modules and Interfaces"
Cohesion: 0.40
Nodes (4): Frozen evidence, Interpretation boundary, Operational changes, Team 8 refresh - 2 September 2026

## Knowledge Gaps
- **468 isolated node(s):** `Black–Scholes/GBM constant-volatility gold benchmark`, `Barrick Mining research repository, revised October 5, 2026`, `Generated outputs`, `Research programme and collaboration`, `Introduction` (+463 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1378 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BatesHawkesExact` connect `Option Pricing and Calibration` to `Option Pricing and Calibration`, `Option Pricing and Calibration`, `Option Pricing and Calibration`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **Why does `ExactHawkesCalibration` connect `Physical Models and Admission` to `Option Pricing and Calibration`, `Option Pricing and Calibration`?**
  _High betweenness centrality (0.000) - this node is a cross-community bridge._
- **Why does `Bates` connect `Option Pricing and Calibration` to `Option Pricing and Calibration`, `Option Pricing and Calibration`, `Option Pricing and Calibration`?**
  _High betweenness centrality (0.000) - this node is a cross-community bridge._
- **What connects `Black–Scholes/GBM constant-volatility gold benchmark`, `Barrick Mining research repository, revised October 5, 2026`, `Generated outputs` to the rest of the system?**
  _468 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Physical Models and Admission` be split into smaller, more focused modules?**
  _Cohesion score 0.04188144329896907 - nodes in this community are weakly interconnected._
- **Should `Frozen Research Reference` be split into smaller, more focused modules?**
  _Cohesion score 0.05350140056022409 - nodes in this community are weakly interconnected._
- **Should `Frozen Research Reference` be split into smaller, more focused modules?**
  _Cohesion score 0.07876712328767123 - nodes in this community are weakly interconnected._
## Scientific and coverage boundary

The graph indexes canonical Python source/tests and the document topology of both reports, with curated semantic evidence for copper, probability measures and physical-model diagnostics. TeX headings, inclusion and publication-image relationships are explicit lexical topology, not a new mathematical audit. Frozen reference code remains distinguishable by its source paths. Licensed observations, local price rows, logs, archives and duplicate builds are excluded. Image nodes declare referenced deduplicated publication assets; no new visual empirical inference is made.

Restricted physical coefficient maps and a training-only historical P GBM baseline are implemented. Fixed-current-Q richer fits remain in-sample, exploratory and numerically unconverged. The exact constant-tilt CIR/nonmark-dependent Hawkes family now has a conditional finite-horizon joint-density proof. This theoretical result does not establish empirical identification, discrete-likelihood convergence, origin-only richer physical OOS, reconciled FCFF or corporate value. The Heston refit remains NOT_DCF despite optimizer success. The frozen R scenario results retain their separate status.

Original repeated endpoint relationship records are retained in extraction.json. Explicit unresolved AST import boundaries are declared as external stubs, not treated as implemented modules. Host semantic token usage is unavailable; zero means unmetered. The dated 20261005/06 snapshots are preserved.

## Dated physical forecast extension

Thirty observed origin surfaces support conditional two-stage recalibration, without current-Q leakage. The single-origin Heston pilot is executed but not model validation; a 29-origin GBM panel has no RMSE advantage over no-change. Joint maximum likelihood is not mandatory; shared option-estimated initial states and omitted uncertainty are explicit. Fixed-delivery expiry and the September valuation stub constrain revenue/DCF integration. The completed 29-origin GBM/Heston comparison and its origin-only gold-basis conversion are indexed. Neither model improves RMSE over no-change. Two Heston optimizer failures remain in the evaluation. Bates and Bates-Hawkes panels are complete and their matched results are indexed below.

## Completed four-family panel, 11 October

Both jump-model jobs completed on 9 October. All four models share 29 physical targets; Hawkes has a small descriptive RMSE advantage, with only 25/29 coverage at nominal 95% for both jump models. Numerical seed sensitivity remains material. Optional analytical normal-mark integration reduces dispersion in a targeted frozen-parameter stress check but does not establish convergence or replace the frozen OOS panel. No corporate valuation is admitted.
