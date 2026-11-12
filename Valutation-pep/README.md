# PepsiCo DCF — G4

Dalla cartella `Valutation-pep`:

```bash
python -m pip install -r requirements.txt
python -m src.pipeline
```

Il run usa lo scenario base D05. Per scegliere uno scenario:

```python
from src.pipeline import run_pipeline
res = run_pipeline(scenario="bear")  # bear, base, growth
print(res["price_mean"])
```

Per esportare i tre scenari senza calcolare la valutazione:

```bash
python -m src.revenues.scenarios --output output/d05_reference.csv
python -m src.revenues.calibration --output output/sigma_calibration.json
```

D04 v2 contiene i ricavi storici G1; sigma è ricalcolata dai livelli (5,2943%).
D05 contiene gli scenari consegnati da G1 e sostituisce la crescita sintetica al 4%.
Sono previsioni, non ricavi osservati. Il file originale è in `data/d05/`.
I parametri FCFF sono quelli provvisori D07; WACC e ponte usano i moduli G3.
Il run completo resta provvisorio e non va presentato come valutazione definitiva.

Da confermare con G2/G3: D05 usa crescita terminale 2,5%, contro il 2% del
precedente config G3. Il run usa 2,5% e conserva il ROIC G3 al 10%; il rapporto
di reinvestimento converge quindi al 25%. Margine e aliquota terminali restano
quelli D07 (15,5% e 20%). Va confermato anche FY2026 come primo anno rispetto
alla data di valutazione 21/10/2026.
