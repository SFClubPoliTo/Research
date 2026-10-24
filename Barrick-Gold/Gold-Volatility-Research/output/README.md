# Outputs 📊

Generated figures, tables, and CSV outputs for the gold, silver, and macro-financial driver analysis.

## 📄 Contents

| Folder | Role |
| --- | --- |
| `csv/` | Machine-readable regression (including Holm-adjusted p-values), AR/ARMA/ARIMA, unit-root, GARCH model-comparison, fractional-differencing/GPH, stylized-fact, and summary outputs. |
| `figures/` | Correlation, quality-check, conditional-volatility, and long-memory diagnostic figures. |
| `tables/` | LaTeX-ready regression, AR/ARMA/ARIMA, unit-root, descriptive, correlation, GARCH, and fractional-differencing/GPH tables for article integration. |

## 🔁 Regeneration

From the project root:

```bash
python src/main.py --offline
```

Generated files can change if upstream market data or model settings are updated. The files in this folder were regenerated on 24 October 2026 after methodological corrections, so they may differ from the article published on 19 June 2026; see the root README for details. Files whose names begin with `arfima_` keep their names for continuity, but they contain fractional-differencing / GPH results, not an estimated ARFIMA model.
