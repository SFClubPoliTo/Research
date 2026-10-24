# Model and market diagnostics

This folder contains the diagnostic figures and small aggregate tables prepared for the Team 8 article. The assets cover surface quality, sampling, residuals, smiles, simulated paths, Treasury curves, and rolling out-of-sample comparisons.

`figure_manifest.json` records the publication-facing set. Regenerate assets with `src/make_missing_ibkr_figures.py` or the relevant validation script, and verify the resulting image before synchronizing it with Overleaf. Raw market observations and row-level diagnostic CSVs do not belong in Git.

## Complete published inventory

Article tables and manifests:

- `article_numbers.tex`
- `article_percentiles.tex`
- `figure_manifest.json`
- `model_error_summary.csv`
- `normality_stats.json`
- `oos_article_numbers.tex`
- `oos_table_rows.tex`
- `terminal_path_stats.csv`

Calibration and market figures:

- `bates_hawkes_residual_heatmap.png`
- `bates_hawkes_volatility_smile.png`
- `bates_residual_heatmap.png`
- `bates_volatility_smile.png`
- `black_scholes_residual_heatmap.png`
- `black_scholes_volatility_smile.png`
- `gld_return_normality.png`
- `heston_residual_heatmap.png`
- `heston_volatility_smile.png`
- `sampling_comparison.png`
- `usd_treasury_curve.png`
- `volatility_surface_3d.png`

Hawkes, simulation, and out-of-sample figures:

- `bates_hawkes_vs_bates.png`
- `bates_poisson_jump_paths.png`
- `gold_path_stats_by_model.png`
- `hawkes_exact_vs_proxy.png`
- `hawkes_intensity_comparison.png`
- `hawkes_jump_paths.png`
- `online_welch_goyal_cumulative.png`
- `paths_bates_5.png`
- `paths_bates_hawkes_5.png`
- `paths_black_scholes_5.png`
- `paths_heston_5.png`
- `terminal_return_percentiles.png`
- `volatility_state_paths.png`

## Status (24 October 2026)

`make_missing_ibkr_figures.py` regenerated the calibration and simulation assets from the corrected 2 September 2026 calibration (q = 0.40%, nested refinements). `oos_article_numbers.tex`, `oos_table_rows.tex` and `online_welch_goyal_cumulative.png` come from the corrected rolling run of 24 October 2026 (q = 0.40%, same search policy for every model), written by `../Complete-Valuation/src/build_report_fragments.py`. The variance-state figure shows the unclipped full-truncation state, which can dip below zero; only max(v, 0) drives the dynamics.
