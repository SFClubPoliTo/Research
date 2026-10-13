# Physical forecasting plan

The canonical shared plan is [utilities/docs/PHYSICAL-FORECAST-PLAN.md](docs/PHYSICAL-FORECAST-PLAN.md). The restricted finite-horizon density proof is [RESTRICTED-JOINT-DENSITY.md](docs/RESTRICTED-JOINT-DENSITY.md). Physical estimation, OOS validation and corporate FCFF admission remain distinct requirements.

## 11 October 2026 — source layout and figure coverage
Source cleanup moves the 223 frozen source files, including eight historical notebooks, from src/reference to utilities/reference with byte hashes unchanged. Active refactored modules are flat; the five numbered notebooks in src call the shared implementation in utilities/python. Legacy manifest paths remain supported. See utilities/docs/SOURCE-LAYOUT.md.

Required next check: copper images and Q/P measure-change images may be missing or insufficiently incorporated in both report editions. Inventory existing figures, generators, dated inputs, units, measures and report inclusions; identify actual omissions, generate only evidence-supported figures, then compile and visually verify unified and paper editions. This is an open verification task, not a confirmed absence or a completed scientific validation.

## Governing layout correction — 11 October 2026
The user's latest instruction supersedes the earlier source layout: src contains only five numbered ipynb files and no folders. Shared implementations live under utilities/python; frozen studies remain under utilities/reference. The old utilities/notebooks/Main.ipynb is archived locally and replaced by 00_Overview, 01_Data_and_Basis, 02_Options_Q, 03_Physical_P_and_OOS, 04_Valuation_and_Reports. Each notebook dispatches shared stages rather than copying models. Copper and Q/P figure coverage remains a required open audit for both reports.
