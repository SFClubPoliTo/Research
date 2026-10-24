# Component-Driven EBITDA Forecast for Barrick Gold 🧱

📄 Article PDF: https://sfclubpolito.it/pdf-viewer.html?file=Pubblicazioni%2FEBITDA%20forecasting%20in%20gold%20mining.pdf&lang=it

This folder contains the code supporting Article 4 in the Barrick Gold Research track and the Starting Finance Club PoliTo Research article *A Component-Driven Methodology for EBITDA Forecasting in Gold Mining*.

## 👥 Authors

- [Giacomo Scali](https://www.linkedin.com/in/giacomo-scali-abp01/)
- [Jacopo Foralosso](https://www.linkedin.com/in/jacopo-foralosso-6753a2256)

## 🎯 Purpose

The workflow builds Barrick Gold's five-year EBITDA forecast from its components: cost of sales, mine-level production drivers, option-implied gold-price volatility and Monte Carlo EBITDA scenarios.

## 🗂️ Structure

| Folder | Role |
| --- | --- |
| `cost_of_sales/` | Log-space ARIMA workflow for forecasting cost of sales per ounce (`cost_of_sales.R`, dependencies in `R_requirements.txt`). |
| `production/` | Bottom-up production forecast from ore processed, average grade and recovery rate, aggregated across mines. |
| `ebitda_montecarlo/` | Black-Scholes inversion of GLD option prices, the implied-volatility term structure, gold-price simulation and the final EBITDA distribution. |

## ⚙️ Setup

**Python** (notebooks). Use Python 3.12; the pinned versions were tested with 3.12.10.

```bash
pip install -r requirements.txt
```

`requirements.txt` pins numpy, pandas, scipy, matplotlib, seaborn, plotly, openpyxl, pmdarima, nelson-siegel-svensson, ib_insync and ipykernel. Use any Jupyter front end to run the notebooks.

**R** (`cost_of_sales/cost_of_sales.R`). Tested with R 4.6.1. Packages and tested versions are in `cost_of_sales/R_requirements.txt`:

```bash
Rscript -e 'install.packages(c("dplyr","tidyr","ggplot2","lubridate","zoo","forecast","tseries"), repos="https://cloud.r-project.org")'
```

## ▶️ Usage

Run the components in this order. Later steps read the files written by earlier ones.

1. **Cost of sales.** `Rscript cost_of_sales/cost_of_sales.R [COST_CSV] [WEIGHTS_CSV] [OUTPUT_DIR]`. Without arguments it reads `cost_of_sales/data/cost_of_sales.csv` and `cost_of_sales/data/cost_of_sales_weights.csv`, and writes `cost_of_sales/output/cost_forecast_global.csv` and `cost_forecast_by_mine.csv`. Non-interactive R saves the plots to `Rplots.pdf` in the working directory. The rolling-origin validation takes a few minutes (about 2.5 minutes on 36 quarters).
2. **Production.** Run `production/production_forecast.ipynb` with `production/` as the working directory. The last cell writes `production/output/production_forecast_total_quarterly.csv`.
3. **Implied volatility.** Run `ebitda_montecarlo/IV_gold_price_BS_inversion.ipynb` with `ebitda_montecarlo/` as the working directory. The **IB** cell downloads a new option chain when you execute it. Skip it if you already have the 2 April 2026 chain files in `ebitda_montecarlo/data/`. The cells write `data/gld_chain_clean.csv`, `data/gld_chain_with_iv.csv`, `data/gld_iv_dataset_200_600.pkl` and `data/gld_iv_curves_200_600.png`. The plotly surface cell opens a browser tab.
4. **EBITDA Monte Carlo.** Run `ebitda_montecarlo/ebitda_mc.ipynb` with `ebitda_montecarlo/` as the working directory. It reads the outputs of steps 1–3. If the cost or production export is missing, it warns and falls back to the arrays used in the 8 May 2026 article.

## 📦 Data needed to reproduce

None of the input files are committed. Put them at these paths (relative to this folder):

| File | Content and columns | Source |
| --- | --- | --- |
| `cost_of_sales/data/cost_of_sales.csv` | One row per mine-year: `Miniera` (mine name), `Anno` (year), `Q1`, `Q2`, `Q3`, `Q4` = **cost of sales per ounce sold** (US$/oz). Use `N/D` or an empty cell for missing values. The script uses quarters from 2017 Q1 onwards; the aggregated series must have no gaps. | Barrick quarterly reports / MD&A and "Mine Stats" operating tables, https://www.barrick.com/English/investors/ |
| `cost_of_sales/data/cost_of_sales_weights.csv` | Same layout and mine names; values = **gold ounces sold** in that mine-quarter, on the same basis (attributable or 100%) as the cost per ounce. Used as weights. | Same Barrick quarterly reports / Mine Stats |
| `production/data/Quarterly Data.xlsx`, sheet `Dati_P` | Columns **in this order**: `Nome miniera`, `data` (quarter as `Q1 2019`), `ore processed` (tonnes), `average grade` (g/t), `recovery rate` (fraction, 0–1). Mine names must match `MINES` in the notebook: Carlin, Cortez, Turquoise Ridge, Pueblo Viejo, Loulo-Gounkoto, Kibali, North Mara, Bulyanhulu. The original workbook is private; rebuild this sheet from the public reports. | Barrick quarterly reports / MD&A and Mine Stats, https://www.barrick.com/English/investors/ |
| `ebitda_montecarlo/data/gld_chain_wide_chain.csv` | GLD option chain of **2 April 2026**. Columns used: `expiry_ymd` (or `expiry_iso`), `T` (years to expiry), `right` (`C`/`P`), `K`, `price_used`. The IB cell also writes bid/ask/mid/last/close/model-price/greeks columns. | Interactive Brokers API (TWS or IB Gateway, delayed data) via the IB cell. Licensed data, not redistributed. Running the IB cell today gives today's chain, not the 2 April 2026 one. |
| `ebitda_montecarlo/data/gld_chain_wide_meta.json` | Fetch metadata; key `S0` = GLD share price at the fetch. | Written by the same IB cell |

The notebooks also contain hand-entered inputs. The Treasury par yields are in the **RATE** cell of the IV notebook (source: US Treasury daily par yield curve; the link is in the notebook). The gold spot `S0 = 4677` $/oz is in `ebitda_mc.ipynb`.

## 🛠️ Corrections (24 October 2026)

1. **`cost_of_sales.R` could not run.** It contained `read.csv("")`. Input paths now come from command-line arguments, with defaults under `cost_of_sales/data/`. Missing files or columns stop the script with a clear message, and the expected columns are documented in the script header.
2. **Undocumented dependencies.** Added `requirements.txt` (Python, pinned to the tested versions) and `cost_of_sales/R_requirements.txt` (R). The Setup section now matches both. `openpyxl`, needed by `read_excel`, was missing before.
3. **Unweighted mean across an unbalanced mine panel.** The company-level cost series was a simple mean of mine-level cost per ounce. It is now weighted by gold ounces sold, which equals total cost of sales divided by total ounces for the mines reported in that quarter. This needs the new weights file. `WEIGHTING <- "equal"` reproduces the published series only.
4. **Validation used a different model than the forecast.** The hold-out test used a fixed ARIMA(3,1,0) with drift, while the forecast used `auto.arima`. Both now use one function, `fit_cos_model()`: `auto.arima` re-selected on the training window. A rolling-origin cross-validation (`tsCV`, expanding window, refit at every origin, h = 1–4 quarters) was added with a naive benchmark.
5. **EBITDA Monte Carlo (`ebitda_mc.ipynb`).**
   - Volatility now comes from `data/gld_chain_with_iv.csv`. The notebook takes ATM implied vols by expiry, interpolates total variance in maturity and converts it to per-quarter forward vols. It replaces the hand-typed `sigma_curve`, which applied term vols as step vols and was never linked to the CSV the notebook loaded.
   - The drift is now a documented physical-measure parameter, `MU_ANNUAL` (default 0). It replaces the risk-free Nelson-Siegel-Svensson curve, which is a pricing (risk-neutral) drift and not a forecast.
   - Cost-of-sales and production uncertainty were added as lognormal shocks, calibrated on the forecast standard deviations exported by the R script and by the production notebook (configurable fallbacks).
   - The cost definition is now explicit. The input is cost of sales per ounce, not AISC and not cash costs. Cost of sales includes D&A, so `DA_PER_OZ` adds it back. With the default of 0 the output is labelled as a revenue-minus-cost-of-sales proxy.
   - The first quarter was fixed at spot. Every quarter is now simulated.
6. **README.** The article number is corrected (Article 4; Article 5 is the Three-Stage DCF). Setup, Usage and Data sections were rewritten.

Compatibility fixes made along the way:

- The IB and IV cells wrote to `Data/` but read from `data/`, which breaks on case-sensitive file systems. Both now use `data/`.
- `groupby(axis=1)` was removed in pandas 3 and is replaced in the production notebook.
- A read-only array passed to `nelson_siegel_svensson` under pandas 3 is now copied.
- The production notebook now exports its quarterly total and standard deviation.

**Effect on published figures.** The forecasts and EBITDA ranges in the article of 8 May 2026 were produced by the previous code. The corrected code was validated on synthetic inputs only, because the input data above are not available in this repository. The article's numbers have **not** been regenerated, and the fallback cost array in `ebitda_mc.ipynb` still comes from the unweighted cost chain.

## 📊 Data

Operational inputs were extracted from Barrick Gold Corporation quarterly reports:

https://www.barrick.com/English/investors/

The development workbook `Quarterly Data.xlsx` is not committed because it contains private working notes. GLD option-chain data were retrieved through the IB API on April 2, 2026 and are not redistributed here.

## 🧪 Reproducibility Notes

- Public source documents must be downloaded again from the original providers.
- Local working files and private spreadsheets are intentionally excluded from Git.
- The material is for research and education only and does not provide investment advice.

## 📚 Citation

Scali, G. and Foralosso, J., *Component-Driven EBITDA Forecast for Barrick Gold: supporting code*, Starting Finance Club PoliTo Research, GitHub repository, published 08/05/2026, accessed 30/05/2026.
