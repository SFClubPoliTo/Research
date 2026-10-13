# Physical forecasting: implemented diagnostics and admission conditions

The objective is physical commodity prices, attributable revenues, reconciled FCFF and compatible corporate discounting. The current valuation CLI still runs the frozen artificial scenario operator. Its physical research metadata does not enable a P valuation.

## Chronological initialization update, 9 October

Further numerical check: `integrate_poisson_counts=True` integrates the daily
Poisson count mixture as well as Gaussian marks when excitation alpha=0.
The implementation rejects self-exciting Hawkes, sums count probabilities
with omitted mass at most1e-12 and preserves the legacy default. The
one-step likelihood matches the analytic compound-Poisson normal mixture
within1e-10. On the same frozen Bates24July stress case, maximum seed NLL
spread falls to17.78 (16steps14.42;32steps17.78), from455.38 originally and
152.97 with marks alone. Remaining variance-particle sensitivity is material.
`20261011-integrated-counts-stress` is a diagnostic, not a refit or replacement
of the completed OOS evidence. The current reports describe the completed
panel and marks-only check; incorporate this additional count result at the
next consolidated numerical-method revision.

The 11 October numerical follow-up adds optional `integrate_marks=True` to
the Euler particle filter. Conditional on counts and variance innovations,
normal marks enter observation mean as N*mu_P and variance as N*sigma_J^2;
they do not feed the latent states in this restricted model. The old default
is preserved. Two tests verify the one-step Poisson-normal mixture and exact
zero-jump parity. The stress run `20261011-integrated-marks-stress` evaluates
frozen premia at each jump family's largest original seed-spread origin
(24 July). Maximum seed spreads over 16/32 substeps decline from455.38 to152.97
for Bates and from402.10 to139.39 for Hawkes. This remains unstable and is
not a refit or a new OOS comparison. Next: count integration/importance
proposals, particle scaling and parameter uncertainty, preserving old freezes.

Completed-panel update (11 October): both supervisors completed on 9 October,
with 28 Q and 28 P JSONs per jump family, plus the separate 10 July pilots.
The four-model intersection has 29 targets and no unmatched observations.
`20261011-four-model-complete` and `20261011-four-model-gold-complete` freeze
the results and source hashes. Gold RMSE GBM/Heston/Bates/Hawkes is
66.3464/66.7737/66.8358/65.8131 USD/oz versus 66.0857 for no-change.
Gold 95% coverage is 27/29,27/29,25/29,25/29; 80% is 21/29,20/29,17/29,16/29.
Two Heston and one Hawkes optimizer failures remain included. The saved-link
audit verifies 58 Q/P links and 49 backward warm-start links. Only 10/29,
6/29 and 9/29 Heston/Bates/Hawkes origins improve the independent likelihood
over zero premia under every seed/grid check; maximum within-grid seed NLL
spreads reach 6.08/455.38/402.10. Numerical convergence, uncertainty propagation,
copper term structure and reconciled corporate FCFF remain separate work.

The origin Q runner now initializes Heston, Bates and Bates--Hawkes from the
latest successful strictly earlier calibration in the same experiment. Missing
calendar days use the latest available origin. The first fit uses the original
global search. Heston and Bates first try constrained local optimization, with
global fallback on failure, inadmissibility or a worsened current-surface loss;
Hawkes uses its previous-origin local branch with fallback if both local starts
fail. Current-origin nested candidates are retained. The general option OOS
calibrator also initializes Heston/Bates chronologically, alongside its existing
Hawkes initialization. Forward latent states are still re-estimated at each
origin; previous parameters are optimizer guesses only.

The physical-premium runner compares the previous successful origin's premia
with zero premia on the current training likelihood, uses the better start and
retains it if optimization worsens it. The zero-premium independent diagnostics
remain zero-premium comparisons. Source date/hash, initial premia and pricing
implementation hashes are recorded; completed old artifacts are retained.
`--cold-start` on the split Q/P runners reproduces the previous initialization
policy. A resumed panel therefore records the policy per origin rather than
claiming that all origins used the new method. New JSON writes are atomic.

The numerical check `20261009-warm-start-check` fits the 14 July surface from
13 July parameters. Total warm times were approximately 0.04/0.28/27.11 seconds
for Heston/Bates/Hawkes. Losses were 2.00094e-5/1.11038e-5/7.18912e-6 versus
frozen cold-fit losses 1.88437e-5/7.55374e-6/7.18960e-6. This checks execution
and exposes local-minimum sensitivity; it is not a controlled speedup estimate,
an equivalent-solution claim, model selection or physical-DCF admission.

## Implemented on 6 October 2026

- `physical_measure.py`: restricted correlated-Brownian, CIR, normal-mark and exponential-Hawkes coefficient maps. Algebraic tests alone do not prove the density martingale. The 7 October restricted joint-density argument now supplies a finite-horizon construction under its explicitly stated assumptions.
- `physical_gbm.py`: irregular-calendar historical GBM likelihood and conditional drift uncertainty.
- `physical_filter.py`: substepped latent-state particle likelihood; fixed-current-Q fits are exploratory, in-sample and not historically origin-calibrated.
- `futures_history.py`: origin-only delivery selection, same-delivery returns and explicit target exclusions.
- Gold basis: 1,003 synchronized observations including nine shortened exchange sessions; 250 missing GLD dates excluded.
- Copper history: seven deliveries, 408 accepted returns; four requested earlier deliveries unavailable. The available universe does not reconstruct historical front-month futures or spot.
- Physical gold baseline: 750 daily and 689 overlapping 90-day targets. All fits precede their targets; current Q parameters are not used. Nominal interval undercoverage is reported, not hidden.
- Filter refinement: 4,096 particles, three seeds, 1/2/4/8 substeps. Material discretization and simulation sensitivity remains. Do not select a winning model from these likelihoods.

## Reproduction

Raw licensed observations stay under `data/raw/ib_local/physical_history_20261005` and are not distributed. Access to those exact local freezes is required to recompute the numerical diagnostics. Public aggregate summaries and hashes are under `outputs/physical_measure`. The dated Q reference is under `data/processed/physical_measure/q_reference_20260902`; it is used only for conditional current-fit diagnostics.

Run the local tools in this order: `audit_gold_physical_basis.py`, `build_copper_physical_history.py`, `fit_physical_gbm_diagnostic.py`, `fit_physical_candidates.py`, `check_physical_filter_convergence.py`, `validate_gold_physical_baseline.py`. The particle stages additionally require the archived official Treasury XML history. Re-running an exploratory diagnostic overwrites its local diagnostic output; preserve a snapshot first when comparing versions. The frozen valuation outputs are not modified by these tools.

## Remaining scientific conditions

A same-underlying P/Q estimator must reconcile continuous diffusion parameters and specify its current latent state, verify that the exact fitted specification and initial-state law satisfy the restricted joint-density proof for the selected horizon (or provide a new proof outside that family), assess premium identification and uncertainty, and pass numerical refinement. Joint maximum likelihood is one possible estimator, not a logical requirement of the measure change. A conditional two-stage estimator may first calibrate Q on origin-date options, then estimate P premia from origin-available returns holding those structural coefficients fixed. It must be labelled as such and account for uncertainty from both stages before claiming unconditional predictive coverage. Copper Bates currently has zero Q jump intensity: an equivalent change cannot invent P jumps. Every richer-model historical forecast requires origin-available calibration, filtering and estimation, never the current Q fit applied to earlier origins.

A P-only historical baseline is a valid separate forecasting benchmark, not evidence that the option-calibrated models have passed physical OOS. Option repricing, commodity prediction and Barrick operating/FCFF prediction are distinct validation targets. Quarterly overlapping errors are not independent observations. Physical expected commodity prices must still be mapped to Barrick realized selling prices, sales and accounting. Independent WACC simulations do not identify a stochastic discount factor. No final company value or target is reported by this work.

## 7 October: shared infrastructure and restricted joint density

Commands are routed through `python -B utilities/python/main.py`. The shared tree passes133offline tests. The full and condensed reports draw on69publication assets; standaloneZIP archives compile independently. The detailed proof is in [RESTRICTED-JOINT-DENSITY.md](RESTRICTED-JOINT-DENSITY.md), with executable coefficient checks in `restricted_joint_entropy_bound` and dated aggregate results under `outputs/physical_measure/20261007-joint-density`. This closes the density-construction question for the stated exact CIR/normal-mark/unmarked-linear-Hawkes family on finite horizons. It does not validate its discretized estimator, risk premia, historical forecasts or corporate cash flows.

A Heston refit at512particles/16substeps/two training seeds reports optimizer success after78evaluations. Independent1024particle checks at16and32substeps do not show a robust improvement over the initial candidate: paired NLL differences change sign across seeds. Optimizer success alone remains insufficient. New run records preserve that result, including the pilot that exhausted its evaluation budget. No new valuation or per-share value has been produced.

## Historical origin experiment and forward paths

The shared suite now passes 140 tests. An observed-field whitelist recovers 30 dated option surfaces with 64 contracts each from the frozen rolling table. Prior model predictions and common-support flags are excluded. All origin spots agree with independently acquired GLD RTH closes. The observed legacy price fields are not asserted to be transaction prices. Recovery does not itself recover historical calibrated parameters: Q must be recalibrated separately at every origin.

`validate_heston_physical_origins.py` implements a conditional two-stage experiment. Each origin uses a generic, future-independent Q initialization and only returns ending by that origin. The forward variance is the same origin option-estimated state under both measures. The historical return filter instead starts at its stated physical long-run mean; its terminal estimate is not silently substituted for the option state. This is an explicit conditioning choice, whose uncertainty and empirical adequacy still require assessment. Independent likelihood seeds and a doubled time resolution are recorded. Target prices enter only after estimation. This experiment predicts GLD prices, before the separate gold-basis and realized-sales transformations.

`physical_paths.py` implements all four forward families with explicit physical premia and instrument identity. A fixed-delivery copper future cannot be simulated beyond expiry or assigned a nonzero pricing drift under the deterministic-rate convention. Rotating-delivery copper returns do not by themselves identify the physical law of the current contract or a five-year spot path. A term-structure/basis model remains necessary for long-horizon copper revenues.

The valuation clock also requires a separate correction: a 2 September valuation cannot discount already elapsed 2026 Q1/Q2 cash flows as future flows. The remaining Q3 stub and subsequent quarters must be aligned with the date of balance-sheet claims. Neither a new P path nor a new model label automatically repairs the frozen twenty-quarter scenario calculation.

Completed origin evidence: the Heston 10 July pilot forecasts 13 July using 1,214 earlier returns and 64 origin options. Both optimizers report success; independent fitted-minus-zero-premium NLL differences span -5.55 to +0.62. Its single GLD forecast error is 10.97 USD/share versus 9.88 for no-change. One forecast cannot establish predictive performance. The larger origin panel is running separately and has not yet been aggregated.

The exact GBM conditional two-stage panel covers 29 next-session targets from 10 July to 1 September origins. Each date has a fresh option volatility fit and an origin-only physical drift fit. RMSE is 6.11915 USD/share versus 6.11743 for no-change; 27 of 29 nominal 95% intervals cover. Mean price-density log score is -3.35405, including the log-price-to-price Jacobian. This short-window result does not establish superiority or long-horizon calibration, and is distinct from the longer historical-only gold baseline.

## 8 October: matched forecasts and gold-unit conversion

All four conditional physical families now have a completed first-origin forecast (10 July to 13 July). Absolute GLD errors are 10.4885, 10.9715, 12.1273 and 9.6653 USD/share for GBM, Heston, Bates and Bates-Hawkes, against 9.88 for no-change. This single case is not a comparative performance finding. The nine-origin GBM/Heston intersection is also frozen separately; neither improves RMSE against no-change on that support. Completed records from interrupted runs are combined by origin/target identity, rejecting duplicates, conflicting target values and future training dates; failed optimizers are not silently discarded after observing errors.

The four forecasts have also been converted to physical gold using a log GLD/gold ratio trend estimated only through the origin. Absolute gold errors on that first target are 114.04, 119.31, 131.91 and 105.07 USD/oz, against 106.45 for no-change. Conversion is applied to the predictive mean and quantiles using a deterministic fitted ratio; basis and parameter uncertainty remain omitted. This is a complete conditional path from dated options and physical returns to a gold-price forecast, before Barrick realized-price, sales and FCFF transformations. It does not imply that the uncertainty or long-horizon law has been validated.

The 146-test shared suite passed before the gold-basis module was added; its two additional future-data-invariance/unit tests passed separately. The larger Heston panel remains in progress. The 7 October Overleaf archives have been independently compiled and their extracted text matches the canonical 209-page unified report and 10-page Paper.

## Completed Heston panel and remaining jump-model runs

The shared suite now passes 148 tests. The Heston background run completed at 13:05 on 8 October, preserving all 19 remaining origin files and its summary. Combining the four disjoint Heston run directories gives all 29 origins with no duplicates or missing targets. `20261008-gbm-heston-complete` records matched GLD RMSE of 6.11915 (GBM), 6.15709 (Heston) and 6.11743 (no-change). Two Heston physical optimisations exhausted their budgets and remain included. `20261008-gbm-heston-gold-complete` records corresponding gold RMSE of 66.34643, 66.77372 and 66.08568 USD/oz. Each model covers 27/29 gold targets at the nominal 95% level. No model superiority is inferred.

The remaining 28 dated Q calibrations and subsequent P fits for Bates and full Bates-Hawkes are launched as separate logged runs. Their pilot origins are already preserved separately. The Q stage must finish successfully before its dependent P stage starts. Each completed date is persisted immediately; no aggregate or completed-panel claim is made while the jobs are still running.

## 11 October 2026 — source layout and figure coverage
Source cleanup moves the 223 frozen source files, including eight historical notebooks, from src/reference to utilities/reference with byte hashes unchanged. Active refactored modules are flat; the five numbered notebooks in src call the shared implementation in utilities/python. Legacy manifest paths remain supported. See utilities/docs/SOURCE-LAYOUT.md.

Required next check: copper images and Q/P measure-change images may be missing or insufficiently incorporated in both report editions. Inventory existing figures, generators, dated inputs, units, measures and report inclusions; identify actual omissions, generate only evidence-supported figures, then compile and visually verify unified and paper editions. This is an open verification task, not a confirmed absence or a completed scientific validation.

## Governing layout correction — 11 October 2026
The user's latest instruction supersedes the earlier source layout: src contains only five numbered ipynb files and no folders. Shared implementations live under utilities/python; frozen studies remain under utilities/reference. The old utilities/notebooks/Main.ipynb is archived locally and replaced by 00_Overview, 01_Data_and_Basis, 02_Options_Q, 03_Physical_P_and_OOS, 04_Valuation_and_Reports. Each notebook dispatches shared stages rather than copying models. Copper and Q/P figure coverage remains a required open audit for both reports.
