# Source Code 🧩

Python scripts for the gold, silver, and macro-financial driver analysis.

## 📄 Files

| File | Role |
| --- | --- |
| `config.py` | Shared paths, ticker symbols, sample dates, and formal variable names. |
| `utils.py` | Shared data-loading, OLS, figure, CSV, and LaTeX-output helpers. |
| `01_data_download.py` | Downloads raw market data from Yahoo Finance. It reuses the frozen raw file when run with `--offline` or when the download fails. |
| `02_data_preparation.py` | Builds clean levels, returns, and yield-change datasets. |
| `03_descriptive_analysis.py` | Produces descriptive statistics, correlations, and quality-check figures. |
| `04_gold_regressions.py` | Estimates gold-return regressions. |
| `05_silver_regressions.py` | Estimates silver-return regressions. |
| `06_stylized_facts.py` | Produces stylized-fact diagnostics and ADF/KPSS unit-root tests. |
| `06b_ar_mean_models.py` | Selects AR(p) specifications (p = 0 to 10, on a common sample) for gold and silver returns. |
| `06c_arma_mean_models.py` | Selects ARMA(p,q) specifications, including ARMA(0,0), for gold and silver returns. |
| `06d_arima_mean_models.py` | Selects ARIMA(p,1,q) specifications, including ARIMA(0,1,0), for gold and silver log prices. |
| `07_garch_estimation.py` | Estimates Gaussian GARCH(1,1), Student-t GARCH(1,1), and GJR-GARCH(1,1,1)-t models with Ljung-Box diagnostics, and exports conditional-volatility outputs. |
| `08_arfima_analysis.py` | Computes fractional-differencing / GPH long-memory diagnostics for absolute returns and tests d = 0, 0.5, and 1. No parametric ARFIMA model is estimated. |
| `09_regression_tables.py` | Builds publication-facing regression tables (Newey-West HAC standard errors, Holm-adjusted p-values) in CSV and LaTeX formats. |
| `main.py` | Runs the full pipeline in order and passes `--offline` on to step 01. |

## ▶️ Run

From the project root:

```bash
python src/main.py --offline
```

The root README section "Corrections (24 October 2026)" lists the changes made after the audit.
