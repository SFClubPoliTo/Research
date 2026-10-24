# Barrick Gold 🪙

📄 Article PDFs are published on the [Starting Finance Club PoliTo website](https://sfclubpolito.it/pubblicazioni). This repository contains public code, documentation, aggregate evidence and reproducibility assets for the Barrick Gold Research programme.

## Articles

| Article | Project | Authors | Publication | Materials |
| --- | --- | --- | --- | --- |
| Article 1 | [Foundations for the Black-Scholes Framework](./Black-Scholes-Foundations/) | Stefano Falcione, Marco Fracca | April 17, 2026 | Mathematical foundations and article metadata. |
| Article 2 | [A Statistical Exploration of Financial Time Series](./OLS-Dynamic-Corr/) | Filippo Triassi, Giorgio Zoccatelli | April 24, 2026 | Reserved empirical companion for time-series and dynamic-correlation material. |
| Article 3 | [Monte Carlo Methods and Portfolio Simulation](./Monte-Carlo-Risk/) | Andrea Rostagno, Francesco Florio | May 1, 2026 | Python package, reproducibility script, figures and CSV summaries. |
| Article 4 | [Component-Driven EBITDA Forecast for Barrick Gold](./Component-Driven-EBITDA-Barrick/) | Giacomo Scali, Jacopo Foralosso | May 8, 2026 | Cost, production, option-implied volatility and EBITDA simulation work. |
| Article 5 | [Three-Stage DCF with Simulated Data](./Three-Stage-DCF/) | Federico Vesco, Lorenzo Pietra, Bader Moussaif | May 30, 2026 | Synthetic DCF, scenarios, charts and CSV outputs. |
| Article 6 | [Beyond Black-Scholes Synthetic Examples](./JumpSVFourier/) | Davide Sisto, Matteo Armando | June 12, 2026 | Jump/stochastic-volatility simulations and reproducibility assets. |
| Article 7 | [Gold, Monetary Regimes, and Volatility Dynamics](./Gold-Volatility-Research/) | Davide D'Amico, Pietro Weisz | June 19, 2026 | Gold/silver econometrics, volatility diagnostics and generated tables. |
| Article 8 | [Advanced Stochastic Modeling for Gold Options](./Gold-Options-Stochastic-Modeling/) | Alessandro Coco, Salvatore Gabriele Messina | **September 4, 2026** | Public Team 8 source package, same-date Treasury curve, aggregate calibration/OOS evidence and figures. |
| Complete Valuation | [Shared research project](./Complete-Valuation/) | Barrick Gold Research Teams | Research in progress | One code and data infrastructure; full unified report and condensed Paper, dated physical-price experiments, operating models and valuation reconciliation. |

## Repository map

```text
Barrick-Gold/
|-- Black-Scholes-Foundations/
|-- OLS-Dynamic-Corr/
|-- Monte-Carlo-Risk/
|-- Component-Driven-EBITDA-Barrick/
|-- Three-Stage-DCF/
|-- JumpSVFourier/
|-- Gold-Volatility-Research/
|-- Gold-Options-Stochastic-Modeling/
`-- Complete-Valuation/
    |-- data/{raw,processed}/
    |-- outputs/{img,parameters,report_unificato,report_paper}/
    |-- src/
    |-- utilities/
    `-- README.md
```

## Reproducibility boundary

The [unified report](./Complete-Valuation/outputs/report_unificato/Articolo.pdf) and
[Paper](./Complete-Valuation/outputs/report_paper/Articolo.pdf) use the same code,
dated inputs, publication images and one generated file of results, so the two
editions cannot quote different numbers. Each report directory includes its LaTeX
source; `src/tools/package_report.py` builds a standalone Overleaf archive locally. The [project README](./Complete-Valuation/)
distinguishes completed numerical experiments from the remaining physical-price
validation and corporate cash-flow reconciliation; the folder name does not
certify a completed company valuation.

- Each project README identifies the runnable entry points and outputs.
- Licensed/provider-controlled row-level option data (IB contract ids, bid/ask, quote times) are kept local and listed in `.gitignore`; public code, hashes, manifests and aggregate evidence remain auditable. They were removed from the tracked tree on 24 October 2026; earlier commits still contain them.
- Historical runs are retained for provenance but are not current unless selected by an authoritative pointer.
- All outputs are educational research sensitivities, not investment recommendations or price targets.

## Corrections of 24 October 2026

An external audit (23 October 2026) led to corrections across the programme. Each affected project README has a "Corrections (24 October 2026)" section; regenerated outputs may differ from the article PDFs published earlier on the club website.

- Article 3: QMC standard error from independent scrambled replications, antithetic gain at equal cost, VaR/CVaR as losses.
- Article 4: runnable R script with documented inputs and dependencies, production-weighted costs, consistent validation, price, cost and production uncertainty in the EBITDA simulation. The input data are not public.
- Article 5: a genuine three-stage DCF, explicit Gordon floor, common random numbers.
- Article 6: compensated jumps, correct multi-jump dispersion, Heston and Fourier pricing checks.
- Article 7: correct fractional differencing, white noise in model selection, GPH tests, unit-root tests, Student-t/GJR GARCH, HAC errors, offline replay.
- Article 8 and Complete Valuation: GLD carry, dated valuation clock, corrected path engines, equal OOS search policy, aligned report editions.

## Citation

Cite the article title, authors, *Starting Finance Club PoliTo Research*, publication status/date, and the exact project folder or immutable run used.
