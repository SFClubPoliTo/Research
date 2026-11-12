# PepsiCo DCF — G4

Dalla cartella `Valutation-pep`:

```bash
python -m pip install -r requirements.txt
python -m src.pipeline
python -m src.revenues.calibration --output output/sigma_calibration.json
```

D13 v2 è conservato in `data/d13/`. Valutazione all’8 ottobre 2026,
prezzo 128,34 USD e ponte al 5 settembre: −42,02079 miliardi USD.
Il primo FCFF annuale è moltiplicato una sola volta per 112/364;
il primo periodo di sconto è 79/364 anni, poi si aggiunge un anno per flusso.
Il terminal value usa l’ultimo fattore di sconto. Crescita terminale 2,5%, ROIC 20%.

Si usano i WACC del YAML D13, uguali per tutti i percorsi: ricalcolarli dal
Python G3 dà una piccola differenza (circa 0,000001 in decimali).
NOPAT terminale e scudo fiscale WACC usano il 21%.

Il run resta provvisorio in attesa del completamento G2/D11.
La pipeline legge la crescita dallo scenario base D05 e ricalcola sigma da D04 v2.
Il valore sigma nel YAML � solo un riferimento. Per cambiare scenario:

```python
from src.pipeline import run_pipeline
res = run_pipeline(scenario="bear")  # bear, base, growth
```

D05 non modifica i parametri G2. Per il confronto deterministico usare
`run_pipeline(override_sigma=0)`.
I vecchi test D07/scenari devono essere riallineati alla nuova interfaccia G2.
Per verificare questa integrazione: `python -m pytest tests/test_d13.py tests/test_sigma.py -q`.
