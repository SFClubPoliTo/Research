# Source modules ⚙️

This folder contains the executable research pipeline for the Team 8 gold-options study.

## Main entry points

| File | Role |
| --- | --- |
| `audit_market_data.py` | Audits date-level coverage and applies the official dense-date admission rules. |
| `ibkr_gld_today_surface.py` | Collects a current GLD option surface through the IB API. |
| `ibkr_gld_historical_surface.py` | Reconstructs bounded historical surfaces through the IB API. |
| `rebuild_full_surface_nss.py` | Rebuilds a dated full surface with the appropriate Treasury curve. |
| `compare_sampling_all.py` | Compares structured 8×8 sampling geometries on one surface. |
| `batch_sampling_offline.py` | Applies the sampling comparison consistently across dates. |
| `calibrate_one_day.py` | Runs and checkpoints all four calibrations for one selected market date. |
| `calibrate_surface.py` | Calibrates the four model families on one admitted surface. |
| `batch_calibrate.py` | Runs resumable calibration across multiple dates. |
| `oos_validation.py` | Performs dense-date rolling-origin calibration and out-of-sample scoring. |
| `make_missing_ibkr_figures.py` | Rebuilds calibration diagnostics, simulated-path figures and `article_numbers.tex` from a frozen calibration, on the q-consistent surface and with full-truncation path engines. |
| `model_smoke_test.py` | Runs a fast deterministic check of the pricing stack. |

## Numerical and shared modules

| File | Role |
| --- | --- |
| `BnS.py` | Implements Black--Scholes call pricing, implied-volatility inversion, and vega. |
| `Heston.py` | Implements Heston characteristic functions, Fourier pricing, and surface calibration. |
| `Bates.py` | Extends Heston with constant-intensity lognormal jumps and calibrated parameter contracts. |
| `BatesHawkesExact.py` | Implements the exact affine Bates--Hawkes pricing engine with state-dependent jump intensity. |
| `Hawkes.py` | Provides Hawkes intensity utilities and exact Bates--Hawkes calibration routines. |
| `Sampling.py` | Builds uniform/Chebyshev 8×8 sampling designs from distinct observed market points. |
| `calibration_core.py` | Defines validated option-surface slices, calibration reports, and feasible optimizer populations. |
| `fourier_pricing.py` | Provides shared Carr--Madan, Gil--Pelaez, and adaptive COS inversion kernels (integration range extended until the characteristic function decays). |
| `gld_carry.py` | Applies the GLD sponsor fee (q = 0.40%) exactly through the forward identity C(S,K;q) = e^{-qT} C(S, K e^{qT}; 0) at the data layer. |
| `dated_initialization.py` | Finds the latest successful strictly earlier fit and converts stored parameters into optimizer vectors for chronological initialization. |
| `rates.py` | Selects no-look-ahead Treasury observations and fits/evaluates Nelson--Siegel--Svensson curves. |
| `surface_builder.py` | Reconstructs historical local surfaces from previously downloaded option, spot, and Treasury data. |

Run scripts from the repository root so relative paths resolve consistently. Generated files belong in `outputs/`, `data/processed/`, or `img/diagnostics_ibkr/`, not here.

The pricing and calibration modules (`Bates.py`, `BatesHawkesExact.py`, `BnS.py`, `Hawkes.py`, `Heston.py`, `Sampling.py`, `calibrate_one_day.py`, `calibrate_surface.py`, `calibration_core.py`, `dated_initialization.py`, `fourier_pricing.py`, `gld_carry.py`, `oos_validation.py`, `rates.py`, `surface_builder.py`) are kept identical to the maintained copy in `../Complete-Valuation/src/pricing/` (last synchronised 24 October 2026).
