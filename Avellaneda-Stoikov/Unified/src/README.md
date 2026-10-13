# Source code 🧩

All operational files are directly in this directory. `main.py` dispatches stages; `layout.py` resolves project paths from the file location.

| Files | Role |
| --- | --- |
| `hft1_*.py` | Classical ABM/GBM, batched Monte Carlo, notebook generation and multivariate figures. |
| `hft2_*.py` | Fractional/Volterra simulation, finite lifts, dashboards, historical scalar HJB and plots. |
| `hft3_*.py` | Positive-policy interpolation, synthetic market/covariance replay and full-residual diagnostics. |
| `figure_replay.py` | Compute/audit the 26 manuscript figures or export original archived assets. |
| `build_reports.py`, `package_reports.py` | Export the manuscript snapshot and compile self-contained report projects. |
| `*.hpp`, `*.cpp`, `CMakeLists.txt` | C++20 full-HJB operators, positive scalar baseline, export and refinement. |
| `00_Overview.ipynb` through `04_Validation_and_Reports.ipynb` | Five curated stage-dispatch notebooks; numerical kernels remain in shared modules. |

Use `python -B src/main.py status` from the project root. For the complete figure computation use `python -B src/main.py run article-figures`. See the root README for inputs, seed qualifications and C++ build commands. Numerical and statistical validation tests are maintained outside the public runtime.
