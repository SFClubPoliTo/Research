# Gold, Monetary Regimes, and Volatility Dynamics 🪙

This folder supports the Starting Finance Club PoliTo Research article on gold, silver, macro-financial drivers, and volatility dynamics from the Gold Standard to modern econometric evidence.

## 👥 Authors

- [Davide D'Amico](https://github.com/0fmate)
- Pietro Weisz

## 🎯 Purpose

The project provides a reproducible empirical pipeline for studying daily relationships among gold, silver, U.S. equities, the U.S. dollar, and long-term U.S. Treasury yields.

The workflow covers data download, cleaning, descriptive statistics, OLS regressions, rolling correlations, stylized-fact and unit-root (ADF/KPSS) diagnostics, AR(p), ARMA, and ARIMA mean-model checks, GARCH, Student-t GARCH, and GJR-GARCH volatility estimation, fractional-differencing (GPH) long-memory checks, and LaTeX-ready output generation.

## 🗂️ Structure

| Path | Role |
| --- | --- |
| `data/raw/` | Raw Yahoo Finance downloads and intermediate level datasets. |
| `data/processed/` | Clean asset levels and return datasets used by the analysis scripts. |
| `output/csv/` | Machine-readable regression, AR/ARMA/ARIMA, volatility, long-memory, and summary outputs. |
| `output/figures/` | Generated charts for correlations, quality checks, volatility, and long-memory diagnostics. |
| `output/tables/` | LaTeX-ready tables for article integration. |
| `src/` | Python scripts for the full empirical pipeline. |
| `requirements.txt` | Python dependencies. |
| `CITATION.cff` | Citation metadata for the code package. |

## 📈 Data

The scripts use Yahoo Finance data for:

- `GLD` for gold;
- `SLV` for silver;
- `^GSPC` for the S&P 500;
- `^TNX` for the 10-year U.S. Treasury yield;
- `DX-Y.NYB` for the U.S. dollar index.

The raw download starts from `2000-01-01`. The common asset-level sample starts on `2006-05-01`, and the effective return sample starts on `2006-05-02`.

## ⚙️ Setup

```bash
python -m venv .venv
pip install -r requirements.txt
```

`requirements.txt` pins the package versions used to regenerate the outputs on 24 October 2026 (Python 3.12).

On Windows, activate with `.venv\Scripts\activate`; on macOS/Linux, use `source .venv/bin/activate`.

## ▶️ Run

From this folder:

```bash
python src/main.py --offline
```

`--offline` skips the Yahoo Finance download and reuses the frozen `data/raw/yahoo_raw_download.csv`, so the outputs reproduce the preserved data. Without the flag, step 01 downloads fresh data and overwrites the raw file. If the download fails or comes back empty or incomplete, step 01 prints a clear message and falls back to the frozen file; it never writes empty CSVs.

The full pipeline runs the scripts in order:

```text
01_data_download.py
02_data_preparation.py
03_descriptive_analysis.py
04_gold_regressions.py
05_silver_regressions.py
06_stylized_facts.py
06b_ar_mean_models.py
06c_arma_mean_models.py
06d_arima_mean_models.py
07_garch_estimation.py
08_arfima_analysis.py
09_regression_tables.py
```

Each numbered script can also be run independently from the project root.

## 📊 Outputs

The pipeline writes processed datasets, descriptive statistics, correlation tables, rolling-correlation figures, OLS regression outputs, stylized-fact diagnostics, AR(p), ARMA, and ARIMA selection outputs, ADF/KPSS unit-root tests, GARCH conditional-volatility estimates, a comparison of GARCH-N, GARCH-t, and GJR-GARCH-t with Ljung-Box diagnostics, fractional-differencing (GPH) long-memory outputs, Holm-adjusted regression p-values, and LaTeX-ready tables.

## 🧪 Reproducibility Notes

- Running the pipeline overwrites files with matching names in `data/` and `output/`.
- The first step relies on Yahoo Finance, so results may vary if upstream data are revised; use `--offline` to reproduce the preserved data.
- Preserved raw data are included to make the pre-publication outputs inspectable without repeating the download step.
- The AR(p), ARMA, and ARIMA modules document conditional-mean diagnostics only; they are not forecasting or investment recommendation tools.
- The article was published on June 19, 2026.
- The material is for research and education only and does not provide investment advice.

## 🛠️ Corrections (24 October 2026)

An internal audit found several methodological and reproducibility issues. The code was corrected and every output was regenerated offline from the frozen raw download. **Regenerated outputs may differ from the article published on 19 June 2026**; where the two disagree, the files in `output/` take precedence.

- **Fractional differencing (step 08).** The filter reversed the weights before `np.convolve`, which already flips the kernel, so the series was filtered backwards in time: with d = 1 it returned minus the first difference. The weights are now applied in their natural order, and a built-in check confirms that d = 1 gives `x_t - x_{t-1}` and d = 0 gives the identity. `arfima_fd_gold.png` and `arfima_fd_silver.png` changed; the estimate of d did not.
- **GPH interpretation (step 08).** The estimates d = 0.576 (gold) and 0.552 (silver) are above 0.5. That places them in the non-stationary, mean-reverting range, not in the covariance-stationary range the earlier note described. The table now tests H0: d = 0, d = 0.5, and d = 1 with the GPH standard error. d = 0 and d = 1 are rejected for both metals (t = 6.39 / 6.91 and -4.70 / -5.60). d = 0.5 is not rejected (gold t = 0.84, p = 0.40; silver t = 0.65, p = 0.51). No parametric ARFIMA model is estimated, so labels now say "fractional differencing / GPH". File names and LaTeX labels are unchanged.
- **White noise in model selection (steps 06b-06d).** The AR, ARMA, and ARIMA grids had left out order 0. With AR(0), ARMA(0,0), and ARIMA(0,1,0) included, AIC and BIC pick the same models for both metals: a constant mean with white-noise errors for returns, and a random walk with drift for log prices.
  - Before: AR p_AIC = p_BIC = 1 (joint F p-values 0.90 and 0.78). ARMA picked (2,0) by AIC and (0,1) by BIC for gold, and (1,0) for silver. ARIMA picked (2,1,0) / (0,1,1) for gold and (1,1,0) for silver.
  - After: every selection is (0,0) or (0,1,0). Gold ARMA AIC -28909.41 -> -28911.33 and BIC -28889.99 -> -28898.42; silver AIC -23448.94 -> -23450.75 and BIC -23429.58 -> -23437.85.
- **Common estimation sample (step 06b).** All AR(p) candidates are now estimated by OLS on the same observations: the first 10 are dropped for every p, so AIC and BIC can be compared. The ARMA and ARIMA candidates already shared their observations under exact maximum likelihood; the code now asserts this.
- **Unit-root tests (step 06).** New ADF and KPSS tests are saved in `unit_root_tests.csv` and `unit_root_tests.tex`. For log prices, ADF does not reject a unit root (p = 0.62 / 0.57 for gold and 0.19 / 0.41 for silver, with constant / constant and trend), and KPSS rejects stationarity (p < 0.01). For returns, ADF rejects a unit root (p < 0.001) and KPSS does not reject stationarity (p > 0.10). These tests replace the AR(1) OLS t-statistic as the reason for differencing once (d = 1).
- **Standard errors and multiple testing (steps 04, 05, 06, 06b, 09).** OLS regressions now use Newey-West HAC standard errors (Bartlett kernel, 9 lags) instead of HC1.
  - The standard errors are about 5-30% larger. For example, gold on the dollar index goes from 0.0450 to 0.0532, and silver on the dollar index from 0.0789 to 0.0958.
  - Only one significance level changes. The univariate gold-equity coefficient (0.0506) drops from the 5% level to the 10% level (p = 0.096).
  - Holm-adjusted p-values for the 12 distinct slope tests are saved in `regression_holm_adjusted_pvalues.csv`. Every coefficient that is significant at 5% stays significant after the adjustment.
- **Constant row (step 09).** The code looked for `const`, but the formula API names the constant `Intercept`, so the "Constant" row was empty in all six regression tables. The row is now filled. For gold it is 0.0003, significant at 5% in the full specification.
- **Volatility models (step 07).** The Gaussian GARCH(1,1) estimates are unchanged. Next to them, the pipeline now also estimates Student-t GARCH(1,1) and GJR-GARCH(1,1,1)-t, with Ljung-Box tests on the standardized residuals and their squares (`garch_model_comparison.csv`, `garch_model_comparison.tex`).
  - Fat tails matter: the estimated degrees of freedom are 5.2 (gold) and 4.4 (silver). BIC falls from 13431.7 to 13112.8 (t) and 13109.1 (GJR-t) for gold, and from 18749.4 to 18341.3 and 18339.1 for silver.
  - The GJR asymmetry term is small and negative (-0.030 and -0.025): positive shocks raise volatility slightly more than negative ones.
  - The Ljung-Box test on squared standardized residuals at 10 lags rejects at 5% for gold GJR-t (p = 0.0008), for both silver t-based models (p < 0.001) and for Gaussian silver (p = 0.045), but not for gold GARCH(1,1)-t (p = 0.068) or Gaussian gold (p = 0.83); some volatility dynamics remain unmodelled.
  - The figures and forecasts still use the Gaussian model.
- **Reproducibility (step 01, `main.py`).** Step 01 no longer writes empty CSVs when the download fails. It falls back to the frozen raw file with a clear message, or stops with an error if that file is missing. `--offline` is now available, and `requirements.txt` pins exact versions.
- **Environment drift.** With the pinned versions, the uncorrected code reproduces the Gaussian GARCH estimates up to about 1e-8. The layout of `descriptive_stats.tex` and `correlation_matrix.tex` changes slightly because pandas 3 formats `to_latex` differently. The processed datasets are identical. Every PNG is re-rendered by the newer matplotlib, but only `arfima_fd_gold.png` and `arfima_fd_silver.png` change in content.

## 📚 Citation

D'Amico, D. and Weisz, P., *Gold, Monetary Regimes, and Volatility Dynamics: supporting code*, Starting Finance Club PoliTo Research, GitHub repository, expected publication 19/06/2026, accessed 02/06/2026.
