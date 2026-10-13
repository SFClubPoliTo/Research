# Unified Market Making 📊

Shared code and data for the unified HFT study and its condensed paper. The structure follows Barrick's Complete-Valuation workspace, with every operational Python module, C++ source/header and five workflow notebooks directly in `src/`.

## Authors

- Salvatore Gabriele Messina: HFT1/HFT2 source contributions and HFT3.
- Niccolò Soriano: HFT1/HFT2 source contributions.

These credits identify the original research contributions. The unified manuscripts are working drafts; their final publication metadata are separate from this code release.

## Purpose

Follow one inventory-control problem through Markovian diffusion benchmarks, non-Markovian memory, finite OU lifts, scalar-state approximations and full-HJB diagnostics. Each experiment retains its own parameters, random stream and terminal-accounting convention. The framework reproduces the figures used by the accompanying Overleaf projects and records where historical raster reconstruction differs.

## Structure

```text
Unified/
  data/{raw/source_freezes,processed}/
  outputs/{hft1,hft2,hft3,validation,img,report_unificato,report_paper}/
  src/                  # flat: Python, C++20 and five workflow notebooks
  README.md
  requirements.txt
```

| Folder | Contents |
| --- | --- |
| [src](src/README.md) | Stage dispatcher, numerical models, plotting and report generators, C++20 applications/headers and five reader notebooks. No source subdirectories. |
| [data](data/README.md) | Original inputs and immutable manuscript/figure snapshots; source and migration manifests. |
| [outputs](outputs/README.md) | Model-specific JSON/CSV/NPZ results, computed figures, numerical diagnostics and both self-contained report editions. |
| `data/processed/provenance` | Hashes, figure-to-generator mapping, replay audit and verified environment versions. |

Development tests, graph tools, reviews, credentials and local workflow records are maintained outside this publication tree. Historical source freezes retain their original internal paths; executable modules live in the flat `src` directory.

## Setup

Use Python 3.12 and install `requirements.txt`. For identical rendering, install `requirements-replay.txt`; the exact versions used for the checked figure replay are recorded in [the replay manifest](data/processed/provenance/article-figure-replay.json). Numerical simulations need no market API or credential. C++ applications require a C++20 compiler; CMake 3.20 or later is optional. Report compilation requires pdfLaTeX.

```powershell
python -m pip install -r requirements.txt
python -B src/main.py status
```

## Run

Run from this directory:

```powershell
python -B src/main.py run article-figures
python -B src/figure_replay.py audit
python -B src/figure_replay.py restore
python -B src/main.py run audit
python -B src/build_reports.py
python -B src/package_reports.py all
```

`article-figures` executes all six numerical/plotting stages, then compares the 26 scientific figure files referenced by the manuscript chapters. It includes the 5000-path scalar and 3000-path classical multivariate experiments, three historical HJB configurations, positive-policy diagnostics and two-asset covariance experiment. Separate stages are `classic`, `rough-figures`, `rough-hjb`, `temporal-figures`, `market` and `multiasset`. The full run can take several minutes.

`restore` exports the original Overleaf assets byte for byte to `outputs/img/publication/overleaf`; it copies archived figures and is distinct from numerical computation. Report generation always uses the immutable manuscript snapshot, preserving the figures and results originally reviewed. It does not replace historical figures with new random samples.

Start with `src/00_Overview.ipynb`, then follow the other four numbered workflow notebooks. They dispatch the same modules as the command line; expensive stages are disabled until `RUN_STAGE` is explicitly enabled. Paths work from the project root or `src`.

For C++:

```powershell
cmake -S src -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

Applications are `solve_baseline`, `export_policy`, `refine_baseline`, `evaluate_residual` and `evaluate_multiasset`. They implement the scalar positive baseline, time-slice export, refinement and operator evaluation. Supply output paths explicitly when regenerating inputs; the figure replay uses the delivered baseline CSV. Compiler files and local binaries are ignored.

## Outputs and figure fidelity

[Unified draft](outputs/report_unificato/Articolo.pdf) · [condensed draft](outputs/report_paper/Articolo.pdf). Each report directory contains its TEX dependency closure and a standalone Overleaf ZIP. The editable source snapshot is `data/processed/manuscript_authoring`; `build_reports.py` exports it without rewriting the mathematical text from historical concatenated drafts.

The checked local replay reproduces **22 of the 26 scientific figures pixel for pixel**. All 26 original Overleaf PNGs remain available byte for byte. The remaining computed renderings are qualified individually in the [figure replay audit](data/processed/provenance/article-figure-replay.json):

- `hft1-py3.png`: the representative seed 42 was recovered and restored; Monte Carlo seed 3000 and the original parameters are retained. The reconstructed four-panel renderer has minor raster/layout differences.
- `hft1-Corr.png`: identical matrix values, labels and coolwarm scale; the original PDF-extracted raster has a different bounding-box geometry.
- `hft2-img_4.png` and `hft2-img_5.png`: the original random streams were not identified in the received sources. Computed alternatives use seed 123, the same diagnostic definitions, grid/sample sizes, blue/orange colors and single-panel log-log layout. Their samples and numerical curves differ from the archived PNGs; generated CSVs record the plotted values.

Classical scalar seeds are 42 for the representative path and 1000/2000 for Monte Carlo; multivariate Monte Carlo uses 3000. Rough-state figures retain their original H-dependent seeds. Positive E1/E2 policy experiments use seed 42, and the two-asset proxy uses seed 73. No alternative seed is silently substituted into manuscript assets or tables.

Policy interpolation cache entries are tied to the SHA-256 of their source surface; changed inputs invalidate the cache.

The flat-source migration passed 12 numerical tests, 5000 byte-identical policy-offset comparisons, the C++ residual suite's 528 deterministic checks and the scalar/multiasset suites; all five C++ applications compile. Figures and reported summaries were rerun from this checkout. These checks establish software/figure reproduction within the declared scope.

## Scientific interpretation

The full finite OU vector is Markovian; its scalar aggregate generally is not closed. The historical clipped scalar solver is separate from the positive bounded baseline. Neither is presented as an exact non-Markovian optimal-control solution.

The covariance proxy reduces integrated risk in the synthetic replay while lowering mean liquidated PnL and sample CARA certainty equivalent. It is **not fitted P3** and has a higher reconstructed full-residual RMS than the separate baseline. The sample CE-difference bootstrap includes zero. Independent full-state reference validation, derivative/interpolation and simulation-step convergence, correction fitting and the exact NS source remain open. No exchange-latency improvement or market calibration is claimed.

## Citation

Cite the relevant original HFT contributions and the accompanying draft edition. Supporting code: Salvatore Gabriele Messina and Niccolò Soriano, *Unified Market Making*, Starting Finance Club PoliTo Research, [GitHub project](https://github.com/StartingFinanceClubPoliTo/Research/tree/main/Avellaneda-Stoikov/Unified). No article publication date or website PDF link is assigned to these working drafts.
