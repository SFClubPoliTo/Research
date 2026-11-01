# Moduli della pipeline PepsiCo

Eseguire dalla cartella `Valutation-pep` con `python -m ...`, per risolvere gli import `src`.

- `revenues/model.py`: `estimate_sigma`, `simulate_revenues` (convenzioni del playground).
- `fcff/model.py`: `fcff(ricavi, ricavo_base, params)` restituisce la tupla `nopat, reinvest, flussi`;
  implementazione locale di D02 v2, opzione A, da confrontare/sostituire con quella ufficiale G2.
- `rates/model.py`: `compute_enterprise_value`, attualizzazione e collegamenti alle funzioni G3.
- `bridge/model.py`: `compute_equity_and_price`, collegamento al ponte G3.
- `relative/model.py`: riservato a G5, non chiamato dalla pipeline.
- `pipeline.py`: `run_pipeline(config_path="config/config.yaml", is_final_run=False,
  override_sigma=None, g3_functions=None)`.

La configurazione comune usa `fcff_parameters`, come il repository del collega.
I parametri della funzione G2 conservano i nomi italiani definiti in D02.
