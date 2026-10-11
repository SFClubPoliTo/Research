# Copper: storico, modelli e integrazione completata

Il perimetro gold originario escludeva il rame. L'estensione comprende Lumwana (100%), Zaldívar (50%) e Jabal Sayid (50%), con volumi già attribuibili.

Storico disponibile: dieci date acquisite, 7 ammesse, 6 confronti temporali. 480 osservazioni su supporto comune ai quattro modelli; 375 per persistence. È un pilota sulle date indicate: le altre 21 date gold non sono state acquisite, non sono dichiarate prive di dati.

| Data | Quote restituite | Quote utilizzabili | Scadenze | Ammessa |
| --- | --- | --- | --- | --- |
| 2026-07-09 | 100 | 75 | 5 | True |
| 2026-07-10 | 104 | 53 | 5 | False |
| 2026-07-20 | 79 | 74 | 5 | True |
| 2026-07-31 | 75 | 18 | 2 | False |
| 2026-08-03 | 73 | 41 | 5 | False |
| 2026-08-12 | 88 | 82 | 6 | True |
| 2026-08-21 | 100 | 86 | 6 | True |
| 2026-08-31 | 97 | 87 | 6 | True |
| 2026-09-01 | 97 | 65 | 6 | True |
| 2026-09-02 | 99 | 86 | 6 | True |

Risultati rolling (480 osservazioni comuni; 375 per persistence):

| Modello | RMSE IV (bp) | R2 vs media | R2 vs persistence |
| --- | --- | --- | --- |
| Black–76 | 106.48 | 0.002 | -1.294 |
| Heston | 71.46 | 0.458 | -0.422 |
| Bates–Poisson | 70.49 | 0.465 | -0.389 |
| Bates–Hawkes | 67.65 | 0.518 | -0.208 |

Nessuno dei quattro modelli batte la persistence nel rolling. Un R2 positivo contro la media non equivale a un miglioramento contro la superficie osservata.

Robustezza con origine fissa (480 osservazioni comuni; 333 per persistence):

| Modello | RMSE IV (bp) | R2 vs media | R2 vs persistence |
| --- | --- | --- | --- |
| Black–76 | 115.38 | 0.001 | -0.345 |
| Heston | 111.94 | -0.05 | -0.282 |
| Bates–Poisson | 90.94 | 0.337 | 0.193 |
| Bates–Hawkes | 92.56 | 0.334 | 0.182 |

Bates e Hawkes hanno stime positive contro persistence con origine fissa. Il campione è piccolo e coincide con quello rolling: non è una replica indipendente né prova di superiorità stabile.

I test sono condizionali sulle superfici IV, con parametri origin-only, proiezione degli stati, tassi as-of e forward del target. Non sono previsioni fisiche di prezzo o validazione FCFF. I contratti sopravvissuti introducono un limite di universo storico. I timeout non dimostrano assenza di dati.

Valuation primaria, USD milioni:

| Modello | Gold | Gold + copper | Incremento copper | SE media incremento |
| --- | --- | --- | --- | --- |
| Black–76 | 14857 | 17483.6 | 2626.58 | 22.9554 |
| Heston | 14846.9 | 17465.1 | 2618.23 | 39.3626 |
| Bates–Poisson | 14746.3 | 17409.4 | 2663.12 | 40.3685 |
| Bates–Hawkes | 14775.7 | 17417 | 2641.31 | 37.0797 |

[Grafico del confronto appaiato](../Overleaf/img/copper/gold_plus_copper_comparison.png). Barre di errore: errore Monte Carlo della media, non incertezza complessiva.

8192 percorsi appaiati, cinque anni senza terminale; rame con vendite/CoS Q2 congelati. Nessun target per azione. Capex, piani minerari, realised basis, Q/P e bridge societario restano aperti. La baseline gold conserva anche actual societari Q1/Q2 seguiti dal forecast delle otto miniere, e non esclude dal calendario i trimestri già trascorsi: perimetro e date richiedono riconciliazione.

Run autorevole: `Github-Branch/outputs/valuation/20261003-gold-plus-copper-v3-temporal/`. V2 resta il primo esperimento statico e non viene sovrascritto.

Modifiche editoriali dell'utente integrate nel capitolo3 e nei raccordi dei capitoli 10–12, con fonte annuale 2025, precisazioni attribuibili/CoS/sold-versus-produced/IPO e sezioni dati/diagnostiche/sintesi. Il PDF precedente è archiviato. Le tabelle/grafici copper sono generati dai run verificati.
