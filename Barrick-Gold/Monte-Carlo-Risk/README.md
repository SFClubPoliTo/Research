# Monte Carlo Methods and Portfolio Simulation 🎲

📄 Article PDF: https://sfclubpolito.it/pdf-viewer.html?file=Pubblicazioni%2FMonte%20Carlo%20Methods%20and%20Portfolio%20Simulation.pdf&lang=it

Code companion for the Starting Finance Club PoliTo Research article *Monte Carlo Methods and Portfolio Simulation: Theory, Convergence, and Applications to Risk Analysis*.

## 👥 Authors

- [Andrea Rostagno](https://github.com/Andrea-Rostagno)
- [Francesco Florio](https://github.com/Francesco-Florio)

## 🎯 Purpose

This folder turns the original notebook workflow into reusable Python modules for random-number generation, stochastic process simulation, Monte Carlo option pricing, variance reduction, non-Gaussian returns, and portfolio risk metrics.

## 🧠 Methodology

The codebase is organized around compact, reproducible examples:

- pseudo-random and transformed random-variable diagnostics;
- geometric Brownian motion and jump-diffusion path simulation;
- European, Asian, and barrier option pricing with Monte Carlo methods;
- variance-reduction techniques such as antithetic variates, control variates, stratified sampling, and importance sampling;
- Gaussian-mixture returns, VaR, CVaR, and terminal-wealth risk analysis.

## 🗂️ Structure

```text
Monte-Carlo-Risk/
|-- README.md
|-- requirements.txt
|-- src/
|-- examples/
|-- figures/
`-- outputs/
```

## ⚙️ Setup

```bash
python -m venv .venv
pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate`; on macOS/Linux, use `source .venv/bin/activate`.

## ▶️ Run

From the project root:

```bash
python examples/run_reproducibility.py
```

## 📊 Outputs

| Output | Description |
| --- | --- |
| `figures/lcg_uniform_histogram.png` | Uniform pseudo-random diagnostic. |
| `figures/box_muller_qq_plot.png` | Normality diagnostic for the Box-Muller transform. |
| `figures/european_call_convergence.png` | European call Monte Carlo convergence. |
| `figures/asian_call_mc_vs_qmc.png` | Standard Monte Carlo versus quasi-Monte Carlo comparison. |
| `figures/terminal_wealth_distribution.png` | Simulated terminal-wealth distribution. |
| `outputs/monte_carlo_summary.csv` | Summary table for prices, intervals, equal-cost variance reduction, VaR and CVaR as losses, and portfolio risk metrics. |

## 🧪 Reproducibility Notes

- Random seeds are fixed inside the example script.
- The examples use synthetic inputs unless explicitly documented in code.
- Results can change if the number of paths, seeds, or model parameters are modified.
- The material is for educational and research purposes only and does not provide investment advice.

## 🛠️ Corrections (24 October 2026)

An audit found three reporting errors; the simulation code was otherwise correct. Regenerated outputs therefore **differ from the numbers printed in the published article PDF**.

- **QMC standard error** (`src/monte_carlo_risk/option_pricing.py:63-91`, `examples/run_reproducibility.py:125-131`): the Sobol estimate was given an i.i.d. standard error, which does not apply to QMC points. The pricer now uses randomized QMC: 16 independent scrambled Sobol replications of 256 points (4,096 paths, the same cost as the plain MC run), with the standard error computed across replications. Asian call QMC: price 6.1229 -> 6.0797, standard error 0.1368 -> 0.0297 (plain MC: 6.2171, standard error 0.1379, unchanged).
- **Antithetic variance ratio** (`examples/run_reproducibility.py:165-166`): the old ratio compared one antithetic pair (2 payoff evaluations) with one plain draw (1 evaluation). The ratio is now computed at equal cost, N pairs versus 2N plain draws, as `2 * Var(pair mean) / Var(Y)`. `antithetic_variance_ratio` 0.4295 (a 57% gain, overstated) is replaced by `antithetic_variance_ratio_equal_cost` 0.8590 (about a 14% gain).
- **VaR/CVaR as losses** (`examples/run_reproducibility.py:188-222`): the old "VaR/CVaR" were terminal-wealth levels, not losses. They are now losses relative to initial wealth (100): `portfolio_var_95_loss` 25.86 and `portfolio_cvar_95_loss` 32.44 (25.9% and 32.4% of initial wealth). The wealth levels are kept under explicit names: `terminal_wealth_quantile_5` 74.14 (was `terminal_wealth_var_5`) and `terminal_wealth_mean_below_quantile_5` 67.56 (was `terminal_wealth_cvar_5`).
- `figures/asian_call_mc_vs_qmc.png` and `figures/terminal_wealth_distribution.png` were regenerated with corrected content. All other metrics are unchanged, and the other figures were re-rendered with identical content (their bytes differ only because the pinned library versions are used).
- `requirements.txt` now pins the versions used to regenerate the outputs (Python 3.12.10).

## 📚 Citation

Rostagno, A. and Florio, F., *Monte Carlo Methods and Portfolio Simulation*, Starting Finance Club PoliTo Research, GitHub repository, published 01/05/2026, accessed 30/05/2026.
