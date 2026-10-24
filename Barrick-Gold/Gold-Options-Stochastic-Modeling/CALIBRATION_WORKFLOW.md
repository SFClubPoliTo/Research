# Team 8 calibration workflow

This document defines the reproducible calibration and rolling out-of-sample workflow for Black--Scholes, Heston, Bates, and exact affine Bates--Hawkes models.

## 1. Pre-calibration gate

Run the market-data audit before any expensive optimization:

```powershell
python src\audit_market_data.py --start 2026-07-06 --end 2026-09-02 --min-dte 75 --cc-size 64 --min-expiries 3
```

The official dense-date exercise admits a date only when it contains at least 64 unique valid observations after the DTE filter and at least three expiries by default. Sparse dates remain available for coverage analysis but are not padded or duplicated.

## 2. Common sampling geometry

The calibration grid is **fixed a priori** to `CC` (8×8 Chebyshev–Chebyshev nodes, 64 actual observations) at every date and every rolling origin. It is not selected from data. The eight candidate geometries below are compared only as a robustness diagnostic:

| Code | Maturity nodes | Strike nodes |
| --- | --- | --- |
| `UU` | Uniform | Uniform |
| `CU` | Chebyshev | Uniform |
| `UC` | Uniform | Chebyshev |
| `CC` | Chebyshev | Chebyshev |
| `EU` | Exponential | Uniform |
| `EC` | Exponential | Chebyshev |
| `GU` | Gaussian-centered | Uniform |
| `GC` | Gaussian-centered | Chebyshev |

The diagnostic ranks the geometries by holdout maximum absolute implied-volatility error (L∞), with holdout RMSE and MAE as tie-breakers, by interpolating the sampled nodes back to the full surface. This ranking does **not** choose the calibration grid. Under it, `CC` ranks last of eight on 2 September 2026: its holdout L∞ is 242.5 bp against 150.7 bp for the first-ranked `GU`, although its holdout RMSE, 22.7 bp, is mid-table (`outputs/paper_audit_inputs_20260907/sampling/2026-09-02/sampling_comparison.csv`). `sampling_winner.json` records this explicitly: “CC is fixed ex ante for calibration and is not changed by the daily diagnostic ranking”. An earlier version of this document said that the grid was chosen by the L∞ criterion, but the code has never done that. If the article reports the sampling comparison, it must present `CC` as a design choice, not as the winner.

```powershell
python src\batch_sampling_offline.py --start 2026-07-06 --end 2026-09-02 --n-t 8 --n-k 8 --min-dte 75
```

## 3. Single-date calibration

`calibrate_surface.py` reads an admitted surface directly, creates the selected 64-point sample, and writes each model result as soon as it completes. The GLD sponsor fee is applied as a continuous carry `q` (`--dividend-yield`, default 0.0040) through the forward identity C(S,K;q) = e^{-qT} C(S, K e^{qT}; 0) (`gld_carry.py`). Strikes and prices in the frozen `calibration_surface.csv` are therefore rescaled, with the quoted values kept in `K_quoted` and `price_quoted`. Warm starts from an earlier date are opt-in for every model (`--warm-start`, alias `--hawkes-warm-start`); `--no-hawkes-warm-start` is accepted as a no-op. With the flag, Heston and Bates try a local fit from the latest successful earlier date in the same output root, keep it only when it does not worsen the current loss, and otherwise run the global search; Bates–Hawkes starts from the earlier fit under the same rule. Without it, every model runs its own search, so the result does not depend on what else the output folder holds. Every result records `warm_start_used`, `global_search_used` and `initialization_source`. For Bates–Hawkes, `success` means that an admissible candidate was retained; the SLSQP exit status is stored separately in `optimizer_success`.

```powershell
python src\calibrate_surface.py --date 2026-09-02 --surface data\processed\full_surfaces\GLD_2026-09-02_eligible_full_surface.csv --strategy CC --profile full
```

The per-date directory contains a manifest, the exact calibration surface, one JSON result per model, diagnostics, and a compact summary. Successful result files are reusable checkpoints.

## 4. Batch calibration

```powershell
python src\batch_calibrate.py --dates 2026-08-28,2026-08-31,2026-09-01,2026-09-02 --strategy CC --models bs,heston,bates,hawkes --profile full --seed 8
```

The order is Black--Scholes, Heston, Bates, and exact Bates--Hawkes. Bates is retained as the nested jump-diffusion benchmark and as a useful initialization reference. Resume behavior prevents successful models from being recalibrated unless a forced rerun is explicitly requested.

## 5. Dense rolling out-of-sample validation

Preview admitted origins and targets first:

```powershell
python src\oos_validation.py --start 2026-07-06 --end 2026-09-02 --min-dte 75 --min-surface-points 64 --min-origin-expiries 3 --dry-run
```

Run or resume origin calibrations:

```powershell
python src\oos_validation.py --start 2026-07-06 --end 2026-09-02 --min-dte 75 --min-surface-points 64 --min-origin-expiries 3 --profile full --calibrate-only
```

Score the next available dense-date forecasts:

```powershell
python src\oos_validation.py --start 2026-07-06 --end 2026-09-02 --min-dte 75 --min-surface-points 64 --min-origin-expiries 3 --profile full
```

The target is the next admitted dense date, not necessarily the next calendar date. The final admitted date is target-only unless a later target becomes available.

The exercise is a conditional repricing test, not an ex-ante forecast. Parameters and projected states come from the origin, but the target date’s spot and no-look-ahead curve are used when the target contracts are priced. The two benchmarks see different information from the models. The persistence benchmark interpolates the whole origin surface, about 150 valid quotes per date on average, while the models are calibrated on the 64 CC nodes. Comparisons with persistence use only the target contracts inside the origin convex hull: 4,026 of the 4,667 common observations in the legacy run. Pricing exceptions are counted per model in `run_manifest.json`. `paper/rolling_oos_methodology_draft.tex` gives the exact definitions.

## 5a. Calibration fragility

Read the single-date parameters as weakly identified. On 2 September 2026 with q = 0.40% (`../Complete-Valuation/outputs/paper_audit_20261024/calibration_audit.json`):

- the Feller constraint 2κθ ≥ ξ², imposed as a hard constraint, binds at the Bates and Bates–Hawkes optima and is within 0.3% of binding for Heston. Relaxing it lowers the Heston loss by about 68%;
- κ is weakly identified. With the other Heston parameters re-optimised, the loss stays within 3% of the optimum for κ in [2, 4] (`heston_kappa_profile.csv`);
- jump and Hawkes parameters are not individually identified from 64 calls. Only their combined effect on the smile is identified.

## 6. Required run metadata

Every final run must preserve:

- date and exact source-surface path;
- source hash or equivalent immutable identifier;
- full and calibration sample sizes;
- maturity and strike sampling geometry;
- spot and no-look-ahead Treasury curve date;
- numerical profile, objective, model list, and seed;
- success state, elapsed time, parameters, and diagnostics for each model.

The default deterministic seed is `8`. Final results use the `full` profile; `quick` is reserved for smoke and pipeline checks.

## 7. Output and artifact policy

Generated runs belong under `outputs/` and remain local by default. Only reviewed aggregate tables and figures needed by the article may be promoted to `img/diagnostics_ibkr/`. Raw restricted records, credentials, caches, temporary notebooks, and failed or superseded artifacts must not enter the SF GitHub staging or Drive publication package.

Before article synchronization, verify the model smoke test, manifests, figure hashes, and the exact numerical claims transferred to Overleaf.
