# Generated outputs

The current delivered documents are [the unified report](report_unificato/Articolo.pdf)
and [the Paper](report_paper/Articolo.pdf), with sources and standalone Overleaf ZIPs.
Both use the same `img/publication/` figure store and retain explicit scientific limits.

| Path | Role |
| --- | --- |
| `img/publication/` | Shared report figures, deduplicated by content hash. |
| `parameters/` | Namespace for new fitted parameter exports. |
| `physical_measure/` | Dated JSON calibrations, OOS comparisons and numerical diagnostics. |
| `tables/` | Shared CSV/TeX tables. |
| `paper_audit/`, `validation/` | Replay and validation evidence. |
| `report_unificato/`, `report_paper/` | The two report editions. |

Current physical evidence: [four-model GLD comparison](physical_measure/20261011-four-model-complete/summary.json),
[gold comparison](physical_measure/20261011-four-model-gold-complete/summary.json),
and [numerical audit](physical_measure/20261011-four-model-complete/numerical_audit.json).
Each dated experiment keeps its JSON/CSV/parameters and provenance together.
The retained `thesis/20260828T180000Z-unificato-publication/` is a historical
figure run, not the current unified document.

The other retained output families are not alternative thesis versions:

- `current/` contains dated LSE research snapshots;
- `figures/team-8/` contains the frozen-aggregate OOS diagnostic regenerated
  by the autonomous figure runner;
- `valuation/20260825T143500Z-provisional-v3/` is an immutable regression
  fixture whose byte identity is checked by the test suite;
- `valuation/20260826T111412Z-conditional-multimodel-v4-final/` and
  `verification/20260826T205500Z-code012-current-runtime-parity/` are paired
  historical parity fixtures, not current Barrick valuation outputs.

Do not cite regression or parity fixtures as the current valuation. New figures
must have a generator and accepted provenance before entering the shared
`img/publication/` store. Historical file locations remain stable for hash/path
verification; they are not separate report infrastructures.
