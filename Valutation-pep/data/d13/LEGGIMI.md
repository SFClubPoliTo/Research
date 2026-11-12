# Codici e valori per G4 (D13 v2)

Data di valutazione: 8/10/2026 (H01), giorno di uscita di 10-Q e risultati; bilancio del ponte al 5/9/2026. Importi in miliardi di USD, tassi in decimali.

## Contenuto

| Cartella | File | Cosa contiene |
|---|---|---|
| `consegne/` | `D13_config_v2_G3.yaml` | i valori da leggere nella pipeline |
| | `D13_tassi_v2_G3.csv` | tutti i parametri, con fonte e data |
| | `D13_wacc_annuale_v2_G3.csv` | WACC per anno e distanza di sconto |
| | `D13_beta_peer_v2_G3.csv` | beta dei 9 peer |
| `codice/` | `D13_wacc_terminal.py` | WACC, terminal value ed EV |
| | `D13_equity_value.py` | ponte da EV a valore per azione |
| | `beta_calculator.py` | beta dai peer; legge `../dati/D09_peer_beta_v1_G5.csv` |
| `dati/` | `D09_peer_beta_v1_G5.csv` | dati dei peer (G5, D09) |
| | `beta_storico_60m.csv` | beta a 60 mesi 2016–2026, base del beta di maturità |
| `calcoli/` | `calcolo_wacc.ps1`, `beta_storico.ps1` | rigenerano i file di `consegne/` e il beta storico (PowerShell) |

## Valori principali

- WACC: 6,75% nel 2026–2030, 6,82–6,88% nel 2031–2035, 6,88% dal 2036.
- Ponte: −42,021; azioni diluite 1,366; valore per azione = (EV − 42,021) / 1,366.
- g∞ = 2,5%; WACC al 21%; NOPAT al 19% negli anni 1–5, poi converge al 21% (k = 0,5) negli anni 6–10; terminal value al 21% (G2).

## Cosa cambia nel codice

- `ValueCalculator(g_inf, tax_nopat_inf, first_year_fraction, first_discount_period)`: aliquota del NOPAT dell'anno 11 0,21; quota del 2026 112/364; distanza del primo flusso 79/364.
- Nel config quota, distanze e WACC non sono arrotondati, così il run con sigma = 0 ritrova il DCF deterministico.
- Il FCFF 2026 va passato per l'intero esercizio: il codice ne conta solo la quota dopo il bilancio del 5/9 (30,77%).
- Sconto a fine esercizio, a partire dall'8/10: 0,22, 1,22, …, 9,22 anni; il terminal value usa l'ultimo fattore.
- Il WACC è lo stesso in tutti i percorsi e in tutti e tre gli scenari.

## Controllo

Da `codice/`:

- `python D13_wacc_terminal.py` → WACC 0,0675 (crescita) e 0,0688 (maturità)
- `python D13_equity_value.py` → ponte −42,021
- `python beta_calculator.py` → beta di PepsiCo 0,5110 (prima fa un test di regressione su KO: servono `yfinance` e internet)
