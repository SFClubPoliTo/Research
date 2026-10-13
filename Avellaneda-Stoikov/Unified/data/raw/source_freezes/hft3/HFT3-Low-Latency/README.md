# Residual-Corrected Rough-Volatility HJBs 📈

Numerical research code for the HFT3 working paper of Starting Finance Club PoliTo. This increment implements operator diagnostics, derivative-aware correction interfaces and a positive scalar baseline. A fitted corrected policy is not yet available.

## 👤 Author

Salvatore Gabriele Messina.

## 🎯 Purpose

Separate the full-HJB defect caused by state compression from numerical error in the scalar baseline, then develop constrained localized corrections with bounded online cost. The proposed Navier–Stokes connection concerns an algorithmic architecture: its exact source remains unverified and no theorem transfers to this financial model.

## 🗂️ Structure

| Path | Current role |
| --- | --- |
| `include/hft3/full_hjb_residual.hpp` | Common-noise HJB, bounded arrival controls and scalar jet embedding |
| `include/hft3/correction_basis.hpp` | Exact product derivatives and addition of corrections |
| `include/hft3/correction_gate.hpp` | C2 gate with first and second derivatives |
| `include/hft3/scalar_baseline.hpp` | Positive scalar solve with CFL substeps; t=0 output |
| `apps/audit_hft2.py` | Read-only audit of explicitly supplied HFT2 source |
| `apps/evaluate_residual.cpp` | Independent cross-language residual check |
| `apps/solve_baseline.cpp` | Spatial/time refinement diagnostic |
| `tests/` | Deterministic operator and scalar-solver checks |
| `src/main.cpp`, `benchmarks/latency_benchmark.cpp` | Inherited demonstrations with artificial policy surfaces |
| `output/baseline_audit/` | Synthetic samples, residual comparison and refinement table |

## ⚙️ Setup

C++20 and CMake 3.20 or newer for the conventional build. Local verification used the Zig 0.16.0 C++ driver with `-std=c++20 -O2`; CMake configuration is not yet tested locally. The optional HFT2 audit requires Python, NumPy, Matplotlib and the historical HFT2 source identified by its output hash.

## ▶️ Build and run

From this directory, keep build files outside the publication code folder:

```sh
cmake -S . -B ../../Utilities-Progetto/Artifacts/CMake-Build -DCMAKE_BUILD_TYPE=Release
cmake --build ../../Utilities-Progetto/Artifacts/CMake-Build --config Release
ctest --test-dir ../../Utilities-Progetto/Artifacts/CMake-Build -C Release --output-on-failure
```

Run `solve_baseline output/baseline_audit/scalar_refinement.csv` and `evaluate_residual output/baseline_audit/samples.txt` using the executables in that build directory (or its Release subdirectory for multi-configuration generators). The evaluator writes CSV to standard output and exits nonzero on mismatch.

The verified portable compiler route, with `uv` available, is:

```sh
uv run --with ziglang==0.16.0 python -m ziglang c++ -std=c++20 -O2 -Wno-nullability-completeness -I include tests/test_residual.cpp -o ../../Utilities-Progetto/Artifacts/Build/test_residual.exe
```

The same invocation compiles `tests/test_scalar.cpp`, `apps/evaluate_residual.cpp` and `apps/solve_baseline.cpp` to separately named executables. Create the output directory first. Warning suppression addresses nullability diagnostics from the bundled standard library.

Reproduce the inherited baseline audit with:

```sh
python apps/audit_hft2.py --source "../../../Team 2 - Rough Volatility Inventory/Github-Branch/HFT-2/Rough-Volatility-HJB/src/solve_rough_hjb.py"
```

## 📊 Verified results and limits

- 528 deterministic operator/correction checks passed; scalar tests passed for constant and analytic-risk limits, symmetry, positivity and invalid grids.
- C++ agrees with Python residuals on 180 samples; maximum absolute difference approximately `1.16e-10`.
- The inherited baseline saturates clipping bounds extensively. Its large residual is diagnostic, not evidence of correction quality.
- Six transformed-baseline runs use 61/121/241 state points and 2340/4680 time steps without value clipping. Selected-point refinement is encouraging; domain sensitivity and a full residual study remain open.
- No fitted corrector, full time-dependent policy export, economic improvement or latency claim is established. The inherited benchmark uses artificial surfaces and has not been run as an HFT3 performance result.

## 📚 Citation

Salvatore Gabriele Messina, *High-Frequency Market Making under Avellaneda–Stoikov: Residual-Corrected Rough-Volatility HJBs and Low-Latency Control*, Starting Finance Club PoliTo, Research, working draft, 2026.

## Temporal policy export (11 September 2026)

Build the export_policy target (apps/export_policy.cpp), then run `export_policy output/baseline_audit/temporal_policy.csv`. Run `python plots/temporal_policy.py` to check the export and regenerate both article figures plus temporal_validation.json. Dependencies: NumPy and Matplotlib. The deterministic export runs nine domain/grid configurations at 9360 time steps, retaining 41 physical times; CSV blanks mark disabled sides, not zero quotes. Snapshot history is ordered from T to zero; the original theta member remains the t=0 result. The optional history has a 100-million-double allocation guard. No online interpolator or latency claim is supplied by this CSV interface. Tests cover the analytic risk solution at saved times and unchanged t=0 results. Independent residual and temporal convergence validation remain pending before correction fitting.

## Illustrative market application

Run `python apps/simulate_market.py` after export_policy. NumPy/Matplotlib required. This produces E1/E2 session traces, terminal outcomes, summary.json and market_session_E1/E2.png in the article image directory. P2 interpolates theta before applying the bounded Hamiltonian; naive uses the constant zero-gain offset. Each environment has 300 paired paths, 3900 intervals, seed 42; path zero is displayed without outcome selection. Exact OU updates use a spectral covariance factor with a roundoff-only negative-eigenvalue guard. Common marked Poisson candidates allow multiple sequential fills per interval. Frozen-price/volatility event processing is a splitting approximation, with time-step convergence still pending. Tests/assertions cover node interpolation, disabled sides, inventory bounds, accounting and final closeout. This is an illustrative baseline application; no P3 or latency claim.

## Two assets with six volatility factors each

Run `python apps/simulate_multiasset.py` after the existing temporal export. This uses NumPy/Matplotlib and produces output/multiasset CSV/JSON and three article figures. Both synthetic assets have their own six-factor OU lift. Price correlation is 0.7, volatility-driver correlation 0.35, with price and volatility Brownian vectors independent. Separate P2 lookups are compared with an explicit cross-inventory covariance proxy applied to raw quote offsets before clipping. This is not fitted P3 and no full-residual decrease is certified.

Main run: 400 paired paths, 3900 intervals, seed 73, initial inventory (3,0), cash -300, prices (100,100). Mean integrated variance decreases 5.8443 to 4.9608, but mean liquidated PnL decreases 14.4335 to 14.0905; sample CARA certainty equivalent also decreases slightly. Preserve this trade-off. A 1950-step diagnostic is not a convergence certificate; zero-price-correlation regression gives identical policy outcomes. `multiasset_model.self_test()` checks covariance correction gains, terminal preservation, correlation signs, finite-trade risk and invalid PSD rejection. `tests/test_multiasset.cpp` checks the new generic fixed-dimension HJB operator; build target test_multiasset. Caller supplies valid covariance matrices; no leverage terms or per-asset heterogeneous control parameters in this initial C++ specialization. Full specification and limitations: ../../Utilities-Progetto/MULTIASSET.md.
