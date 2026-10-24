# Gold Options Stochastic Modeling 📈

Research code and reproducibility assets for the Starting Finance Club PoliTo article on stochastic modeling, calibration, and rolling out-of-sample validation of gold-option models.

## 👥 Authors

- [Salvatore Gabriele Messina](https://github.com/SalvatoreMessina11)
- [Alessandro Coco](https://github.com/0c0c)

## 🎯 Purpose

The project compares Black--Scholes, Heston, Bates, and an exact affine Bates--Hawkes specification on GLD option surfaces acquired through the IB API. It provides a reproducible path from market-data quality checks and Treasury-curve preparation to structured 8×8 sampling, calibration, diagnostics, and dense-date rolling out-of-sample evaluation.

This repository is research material. It does not provide financial advice or trading recommendations.

## 🗂️ Structure

| Path | Role |
| --- | --- |
| `src/` | Data collection, surface construction, sampling, pricing, calibration, validation, and figure generation. |
| `data/raw/` | Manually supplied source inputs that may be redistributed. |
| `data/processed/full_surfaces/` | Dense option surfaces (kept local, not redistributed) and the versioned Treasury NSS metadata. |
| `data/processed/sparse_historical_surfaces/` | Historical option surfaces (kept local) and the versioned aggregate coverage summary. |
| `img/diagnostics_ibkr/` | Article-ready diagnostic figures and aggregate supporting tables; row-level diagnostic CSVs stay local. |
| `outputs/` | Generated runs; the named September 7 Paper audit directories are versioned. |
| `paper/` | Methodological LaTeX fragments supporting the article revision. |
| `.gitignore` | Explicit curated-data allowlist; environments, credentials, caches and unrelated generated runs remain excluded. |
| `requirements.txt` | Runtime Python dependencies for the published scripts. |
| `CALIBRATION_WORKFLOW.md` | Detailed calibration, resume, and output conventions. |
| `SOURCE_MANIFEST.txt` | Provenance and hashes for the 4 September 2026 clean source snapshot. The modules synchronised on 24 October 2026 no longer match these hashes. |

Folder-level README files document every published file in the corresponding area, together with its role and publication policy. See `src/README.md` for the complete 24-module source index.

## ⚙️ Setup

Python 3.11 or later is recommended. From PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Live collection requires a locally configured IB API session. Credentials and account details must remain outside the repository.

The repository deliberately excludes row-level option quotes. Run the collection/build scripts with your own authorized data access before executing the surface audit, calibration, or rolling validation commands below.

## ▶️ Usage

Run the deterministic model-stack smoke test first:

```powershell
python src\model_smoke_test.py
```

Audit the admitted dense-date universe before calibration:

```powershell
python src\audit_market_data.py --start 2026-07-06 --end 2026-09-02 --min-dte 75 --cc-size 64 --min-expiries 3
```

Preview the rolling design without launching expensive optimizations:

```powershell
python src\oos_validation.py --start 2026-07-06 --end 2026-09-02 --min-dte 75 --min-surface-points 64 --min-origin-expiries 3 --dry-run
```

Run final rolling-origin calibrations with resume support:

```powershell
python src\oos_validation.py --start 2026-07-06 --end 2026-09-02 --min-dte 75 --min-surface-points 64 --min-origin-expiries 3 --profile full --calibrate-only
```

Then compute the rolling out-of-sample scores:

```powershell
python src\oos_validation.py --start 2026-07-06 --end 2026-09-02 --min-dte 75 --min-surface-points 64 --min-origin-expiries 3 --profile full
```

See `CALIBRATION_WORKFLOW.md` for single-date calibration, cross-date sampling selection, manifests, checkpoints, and restart behavior.

## 📊 Outputs

Generated calibration and validation runs are written below `outputs/` and remain local by default. Each completed calibration stores its manifest and model result immediately, so interrupted runs can resume without repeating successful optimizations. Publication-facing aggregate figures and small tables live in `img/diagnostics_ibkr/`.

The implementation enforces the following research controls:

- no look-ahead in Treasury-curve selection;
- a minimum DTE of 75 days for the official dense-date exercise;
- at least 64 unique valid observations and three expiries per admitted origin by default;
- a fixed 8×8 Chebyshev--Chebyshev sample of actual observations, chosen a priori (it is not the winner of the sampling diagnostic, where it ranks last of eight by holdout L∞ on 2 September 2026);
- the GLD sponsor fee as a continuous carry q = 0.40%, applied exactly through C(S,K;q) = e^{-qT} C(S, K e^{qT}; 0);
- no synthetic duplication when market coverage is insufficient;
- the next available dense date, rather than the next calendar day, as the out-of-sample target;
- persistent per-model checkpoints and deterministic seeds.

The rolling exercise is a conditional repricing test, not an ex-ante forecast. Parameters and projected states come from the origin date, but the target date's spot and Treasury curve are used to price the target contracts. The persistence benchmark interpolates the whole origin surface, about 150 valid quotes per date on average, while the models are calibrated on 64 CC nodes. Comparisons with persistence are made on the convex-hull support: 4,026 of 4,667 target observations in the legacy run.

### Calibration fragility

Read the single-date parameters as weakly identified:

- the Feller constraint 2κθ ≥ ξ² is a hard constraint and binds at the optimum. On 2 September 2026 with q = 0.40% it is active for Bates and Bates--Hawkes and within 0.3% of binding for Heston. Relaxing it lowers the Heston loss by about 68%;
- the mean-reversion speed κ is weakly identified. With the other Heston parameters re-optimised, the loss stays within 3% of the optimum for κ in [2, 4];
- jump and Hawkes parameters are not individually identified from 64 calls. Only their joint effect on the smile is.

## 🔒 Data and publication policy

Row-level IB/OPRA option quotes are kept local and are not redistributed. This covers the dense `full_surfaces` and `sparse_historical_surfaces` CSVs, sampling and calibration rows (`sample_*.csv`, `full_eligible_surface.csv`, `calibration_surface.csv`), rolling `option_forecasts.csv`, and the `img/diagnostics_ibkr/diagnostics_*.csv` files. They carry contract identifiers (conId, localSymbol) and quotes. They were removed from version control on 24 October 2026 and are excluded by `.gitignore`. The repository keeps aggregates (coverage summaries, model summaries, date-level metrics, figures), manifests, the Treasury history and the GLD daily close history, and the source hashes in `DATA_MANIFEST_PAPER_20260907.json`. Those hashes let anyone with authorised data access verify a local copy. Account configuration, credentials, caches, environments, legacy backups and unrelated local runs are also excluded. Code belongs in the Research GitHub repository; the SF Drive publication package must contain only the editorial deliverables required by the current publication guide.

## 📚 Citation

Messina, Salvatore Gabriele, and Alessandro Coco. *Advanced Stochastic Modeling for Gold Options: Supporting Code*. Starting Finance Club PoliTo, Research repository, 2026.

The direct article PDF link will be added after publication.

## September 7 Paper audit

The calibration code now preserves better candidates and admits the nested zero-jump and zero-excitation cases. Current-snapshot local refinements are stored separately in `outputs/paper_audit_20260907/parameters/`; original rolling OOS parameters and results have not been recalibrated. For the full offline main runner, tests and operating-proxy figures, use [Complete-Valuation](../Complete-Valuation/).

The manifest paths `team8_data/data/processed/` map here to `data/processed/`; `audit_inputs/outputs/` maps to `outputs/paper_audit_inputs_20260907/`. The original Team 8 manuscript has not been scientifically rewritten by this Paper-focused revision.

## Corrections (24 October 2026)

The numbers in this repository now differ from the article published on 4 September 2026. The published calibration macros could not be reproduced. In them, Bates had a larger IV RMSE (54.63 bp) than Heston (49.49 bp), which is impossible at a nested optimum, and Bates--Hawkes stood at 52.97 bp.

- **Pricing code synchronised** with the maintained copy in `../Complete-Valuation/src/pricing/`. The sync brings in the GLD carry (`gld_carry.py`, q = 0.40% through the forward identity) and chronological initialisation (`dated_initialization.py`). The Bates--Hawkes warm start is now opt-in. A Bates--Hawkes `success` now means an admissible retained candidate, with the SLSQP exit kept in `optimizer_success`. The Fourier integral is no longer truncated at u = 100. Rolling pricing exceptions are counted in the run manifest. Prior-origin warm starts are opt-in for every model (`--warm-start`) and off by default, so in the rolling exercise Heston, Bates and Bates--Hawkes all run their own search at every origin; the corrected run recalibrated Heston and Bates cold after an earlier pass had warm-started them.
- **Calibration figures and macros regenerated**: `src/make_missing_ibkr_figures.py` produced `img/diagnostics_ibkr/` from the corrected 2 September 2026 calibration (q = 0.40%, nested refinements). It prices on the q-consistent surface. Its path simulators mirror `../Complete-Valuation/src/barrick_unified/gold_paths.py`: full truncation with an unclipped variance state, the exact Hawkes intensity integral per step, and drift r − q. IV RMSE on the 64-node CC sample is now 131.58 bp (Black--Scholes), 68.15 bp (Heston), 65.24 bp (Bates) and 52.83 bp (Bates--Hawkes). Bates--Hawkes ≤ Bates ≤ Heston now holds for the calibration loss.
- **Rolling OOS methodology** (`paper/rolling_oos_methodology_draft.tex`) rewritten to describe the code. It now covers 30 near-daily origins targeting the next available dense date, real CC64 calibration sets, and target spot and rates as conditioning variables, so it is a conditional repricing test. It also covers the equal-date R²_OOS, the persistence support versus the model support, and q = 0.40%. In the legacy run (q = 0, Hawkes-only warm start), no model beat persistence. The equal-date R² against persistence was −268% for Black--Scholes, −27% for Heston, −13% for Bates and −3.7% for Bates--Hawkes, and Bates--Hawkes was better on 14 of 30 dates. Inference uses a Diebold--Mariano test with Newey--West variance. The corrected rolling run (q = 0.40%, no model warm-started) enters through `img/diagnostics_ibkr/oos_article_numbers.tex`: mean daily IV RMSE 163.35 / 89.62 / 68.39 / 64.16 bp for Black--Scholes / Heston / Bates / Bates--Hawkes, equal-date R² against persistence −423.9% / −59.0% / −17.5% / −1.8%. No model beats persistence; Bates--Hawkes is statistically indistinguishable from persistence (Diebold--Mariano p = 0.77) and from Bates (p = 0.17).
- **Calibration fragility declared** (see above), and `CALIBRATION_WORKFLOW.md` corrected: the CC grid is fixed a priori and is not chosen by the L∞ holdout criterion, under which it ranks last of eight.
- **Data policy**: row-level quotes were untracked (see the data and publication policy above). `requirements.txt` now pins the reference environment and adds matplotlib.
