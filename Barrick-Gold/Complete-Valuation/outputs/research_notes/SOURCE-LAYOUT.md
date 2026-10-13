# Shared executable source and notebooks

`src` contains the operational implementation: models, acquisition and processing, valuation, and report figure/table generators, alongside five workflow notebooks. The shared packages are `barrick_unified`, `pricing` and `tools`. The `refactored` package has flat prefixed modules instead of seven nested subpackages. Both report editions use this infrastructure. Tests remain in `local development tests`; a generator is not a disposable test merely because it also verifies identities.

Eight notebooks from Teams 4 and 8 are historical source material, now under `data/raw/source_freezes`. Their bytes and original relative structure are preserved; they are not maintained alternative implementations. Their provenance inventory records hashes. Production and margin notebooks describe sequential stages, but merging their frozen originals would invalidate source evidence. The active sequence belongs to the shared Python pipeline.

The five maintained notebooks combine related sequential stages and call the same entry points used by the CLI. They contain no duplicated numerical model code. Each works when opened from the project root or `src`. Execution defaults to a displayed plan; enable it after setting the exact input dates, stage arguments and output IDs. Frozen historical notebooks are not presented as maintained alternatives.

## Figure coverage task — open until checked

Copper figures and figures explaining the Q/P change of measure may be missing or incompletely incorporated. Audit both `outputs/report_unificato` and `outputs/report_paper` against the shared `outputs/img` inventory. Record, per required figure, its generator, dated inputs, units, measure, output hash and inclusion in each report. Existing files alone do not establish coverage.

Check copper futures/spot basis, historical coverage and OOS results; distinguish Q option-surface tests from P price forecasts. Check the Q calibration → conditional P estimation → P commodity/revenue paths interface, shared initial states, and independent numerical-convergence diagnostics. Do not illustrate unavailable five-year copper spot forecasts as validated results. Keep the full explanation in the unified report and selected essential figures in the paper. Generate only figures supported by admitted evidence, then compile and visually inspect both editions.
