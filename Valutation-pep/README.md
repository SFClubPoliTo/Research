# PepsiCo DCF — G4 pipeline
## Struttura

```text
Valutation-pep/
  config/config.yaml
  data/
  output/
  src/
    revenues/model.py
    fcff/model.py
    rates/model.py
    bridge/model.py
    relative/model.py
    pipeline.py
    README.md
  tests/
  requirements.txt
  .gitignore
  README.md
```

Gli output generati sono esclusi dal versionamento, salvo i risultati ricevuti
in `output/d20_consegna/`.

## Installazione e test

Dalla cartella `Valutation-pep`:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

I test verificano l'esempio D02, gli input G2, FCFF e NWC negativi,
la traiettoria deterministica con sigma=0, la media Monte Carlo, il collegamento
della pipeline, il blocco dei dati provvisori e la coerenza al terminale.
Le funzioni G3 usate nei test sono sostituti dichiaratamente sintetici e non
vengono usate dalla pipeline reale. Il benchmark D07 non è ancora disponibile:
il test analitico sigma=0 non sostituisce quel confronto.

## Configurazione e convenzioni

- Ricavo base FY2025: 93.925 miliardi USD, secondo D02 v2.
- Dieci anni espliciti: FY2026–FY2035, cinque crescita e cinque transizione.
  `maturity: 0` rappresenta nessun anno aggiuntivo esplicito: confermare questo
  formato con il costruttore WACC G3. Il WACC di maturità serve comunque al terminale.
- Tassi decimali annuali nominali USD; importi in miliardi USD, azioni in miliardi
  di azioni, prezzo in USD per azione.
- D02 v2 opzione A: negli anni 1–5 reinvestimento da capex, D&A e variazione ricavi;
  negli anni 6–10 vettore fisso `reinv_rate` applicato al NOPAT.
- Margine, aliquota e reinvestimento dell'anno 10 devono coincidere con i parametri
  di maturità G3. Non si sottraggono nuovamente capex e circolante nel terminale.
- Sconto a fine anno con t=1. La data di valutazione originale 21/10/2026 resta
  da allineare con FY2026 come primo anno: non è stata modificata arbitrariamente.

La chiave è `fcff_parameters`. `margine` e `aliquota`
conservano i precedenti valori sintetici; `da`, `capex`, `nwc`, `reinv_rate` e i
tre WACC sono ancora mancanti (`null`). Anche gli importi del ponte sono sintetici.
Per il run finale sia `meta.status` sia `fcff_parameters.status` devono essere `real`.
Cambiare i flag non rende automaticamente reali i dati: vanno prima sostituiti e verificati.

## Collegamento alle funzioni G3

```python
from src.pipeline import run_pipeline

# Inserire qui le vere funzioni o adattatori G3, una volta disponibili.
g3_functions = {
    "build_wacc_path": build_wacc_path,
    "compute_terminal_value": compute_terminal_value,
    "compute_equity_and_price": compute_equity_and_price,
}
res = run_pipeline("config/config.yaml", g3_functions=g3_functions)
```

Questo esempio richiede di importare/definire i tre callable: i nomi del dizionario
sono un contratto locale, non firme già approvate da G3.

| Callable | Argomenti nominati | Output richiesto dall'adattatore |
|---|---|---|
| `build_wacc_path` | `wacc_by_stage`, `stage_years` | vettore `(10,)`, uguale per tutti i percorsi |
| `compute_terminal_value` | `revenues`, `fcff`, `wacc_terminal`, `terminal_parameters` | TV **non attualizzato** a fine anno 10, vettore `(N,)` |
| `compute_equity_and_price` | `ev`, `bridge_parameters` | dizionario con `equity_value` e `share_price`, entrambi `(N,)` |

Il TV viene scontato una sola volta dalla pipeline; l'EV completo viene passato
al ponte. Se G3 restituisce già un TV attualizzato, l'adattatore va concordato e
modificato prima dell'uso. Le voci del ponte hanno importo non negativo e segno
separato ±1; le azioni sono il divisore, non una voce additiva.

Con la configurazione consegnata il run completo si ferma esplicitamente perché
mancano funzioni/dati G3: non inseriamo fallback numerici. I test sono invece eseguibili.

## Elementi ancora da ricevere/confermare

1. G2: implementazione ufficiale `fcff`, vettori provvisori e benchmark D07.
2. G3: funzioni, valori WACC e ponte, firme definitive e convenzione del TV.
3. G2/G3: rappresentazione della maturità terminale e allineamento di t=1 con
   la data di valutazione. Opzione A mantenuta finché non viene concordata B.

## Consegne G1 e G5

- `data/D04_ricavi_v1_G1.csv`: ricavi 2014–2025, rettifiche e riferimenti G1.
  Separatore `;`, importi sia in milioni sia in miliardi USD. La serie omogenea
  è `Ricavi Corretti ($B)`; FY2025 coincide con `r0 = 93.925`.
  Il file viene conservato integralmente, incluse note e fonti.
- `src/relative/d20_intermarket_analysis.py`: script D20 ricevuto da Davide e
  Saverio (G5), senza modifiche alle formule o alle finestre di analisi.
- `data/d20/README_G4.txt`: nota originale di consegna.
- `output/d20_consegna/`: cinque CSV e un grafico ricevuti con D20. Sono risultati
  della consegna, non ricalcolati durante questa integrazione.

Per eseguire D20, dalla cartella `Valutation-pep`:

```bash
python -m pip install -r requirements-d20.txt
cd output
python ../src/relative/d20_intermarket_analysis.py
```

Lo script scarica le serie da Yahoo Finance e richiede una connessione Internet.
Scrive in `output/output_d20/`, separato dai risultati consegnati. Non importarlo
nella pipeline DCF: nella versione ricevuta il download parte all'esecuzione
del modulo. Le dipendenze D20 sono separate da quelle della pipeline.

L'aggiunta di D04 non modifica automaticamente la calibrazione: `sigma = 0.04`
rimane il valore sintetico della configurazione. Per la stima dalla serie G1
va usata la colonna dei ricavi corretti, ricalcolando i log-rendimenti dai livelli
anziché utilizzare quelli arrotondati nel CSV. Lo stato complessivo resta sintetico
finché non sono disponibili tutti i parametri G2/G3.

Prima di aggiornare i risultati D20, confrontare con G5 due punti del codice
consegnato: le etichette 5Y/10Y corrispondono agli intervalli 2020–2025 e
2015–2025; il grafico cumulato usa `(1 + r).cumprod()` su rendimenti logaritmici,
per i quali la ricostruzione coerente è `exp(r.cumsum())`. I file originali sono
stati mantenuti senza rielaborazioni.
