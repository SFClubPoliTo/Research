# D05 — integrazione G1 / G2 / G3 / G4

Consegna ricevuta il 7 novembre 2026. `PEP_scenari.xlsx` e' l'originale G1,
copiato senza modifiche. Importi in miliardi USD, tassi annuali decimali.
La guida assegna D05 (alto/base/basso motivati da prezzo, volume e mercati)
a G2 per i flussi e a G3 per la crescita di lungo periodo; G4 integra i dati.

## Dati effettivamente letti

| Scenario | Crescita FY2026-30 | Crescita FY2035 | Ricavi FY2035 | Celle crescita |
|---|---:|---:|---:|---|
| bear | 1.1319205922% | 2.4572475185% | 110.972006440 | Scenari!D16:M16 |
| base | 3.4463630267% | 2.5295738446% | 127.014986915 | Scenari!D22:M22 |
| growth | 5.6983100719% | 2.5999471897% | 144.477024797 | Scenari!D28:M28 |

Anno base FY2025: 93.925 (B4), uguale a D04 v2 e D02. Il controllo B6=2
seleziona convergenza ricorsiva, k=0.5 in B7: g[t]=g[t-1]+k*(g*-g[t-1]).
Cinque passi FY2031-35; FY2036+ usa g*=2.5% (B5). NON si forza FY2035
esattamente a g*: il piccolo salto nel 2036 e' presente nella consegna.
Il metodo alternativo B6=1 usa il divisore 6, come le formule Excel, non 5.
FX e M&A opzionali B8/B9 sono entrambi zero; non si aggiunge la guidance.
Ipotesi!B32:D32 triangola 50% macro e 50% geografico. Le etichette del foglio
Ipotesi dicono 2027-30, ma Scenari applica questi tassi anche nel 2026: preservato.

## Uso e integrazione

Da `Valutation-pep`, senza G3:

```bash
python -m src.revenues.scenarios --output output/d05_reference.csv
python -m pytest -q
```

Il CSV contiene 30 righe: ricavi, NOPAT, reinvestimento e FCFF deterministici
dei tre scenari; non e' una valutazione finale. I parametri G2 restano provvisori.

`revenues.d05.scenario` nel YAML seleziona `bear`, `base` o `growth` (default base).
Con G3 disponibile: `run_pipeline(g3_functions=..., scenario="bear")`.
L'argomento facoltativo cambia solo quella chiamata; non scrive nel YAML.
Ripetere per i tre scenari mantiene seed e sigma comuni; non assegna probabilita'
agli scenari e non aggrega le tre distribuzioni in una media ponderata.

`src/revenues/scenarios.py` legge l'Excel con la libreria standard, controlla
anni, base, triangolazione, convergenza, FX/M&A, ricavi e ordinamento degli scenari.
I valori memorizzati delle formule sono confrontati con calcoli indipendenti.
E' un adattatore al layout ricevuto, non un motore Excel generico: dopo modifiche
ricalcolare/salvare il workbook in Excel e rieseguire i test. Non valuta tutte
le formule dei fogli informativi ne' verifica esternamente le fonti citate.

La configurazione effettiva viene copiata in memoria. `g_path` e' sostituito
dal vettore D05; `reinv_rate` e' ricostruito con `build_params()` di G2 usando
la crescita dei primi 5 anni e i parametri G2/G3 correnti. Restano invariati
i vettori di margine/aliquota, capex, D&A, NWC, il modulo originale G2 e D04.
Il rapporto reinvestimento/NOPAT converge a g*/ROIC: oggi 12.5%.
La crescita dei ricavi converge ricorsivamente; il reinvestimento continua
a convergere linearmente secondo D07. Sono due grandezze e metodi distinti.
Se g* o ricavo base divergono dalla configurazione, l'adattatore si ferma:
non sovrascrive unilateralmente le decisioni G3 o D04.

L'output `scenario` della pipeline registra nome, fonte, hash SHA256,
anni, celle, tassi effettivi e reinvestimento derivato. Sigma viene sempre
ricalcolata da D04: 0.05294302584051538, non dai percentili macro di D05.

## Compatibilita' D07 e stato aperto

`g_path` al 4% e `fcff_parameters.reinv_rate` nel YAML conservano il riferimento
D07 originale. Con `revenues.d05` presente sono valori di archivio, non quelli
usati dal run attivo. Il comando `python -m src.fcff.reference` continua
deliberatamente a riprodurre D07 al 4%; per D05 usare il comando sopra.
Eliminare il blocco `d05` ripristina il comportamento precedente. I test D07
restano separati e verificano gli stessi numeri ricevuti da G2.

D05 resta `provisional`: l'Excel dichiara data di valutazione 27/12/2025,
mentre il progetto conserva 21/10/2026 in attesa dell'allineamento G3.
Il foglio Controllo_a_posteriori non viene letto nei calcoli; tuttavia Ipotesi!A19
cita Q3 2026 come ancoraggio delle ipotesi geografiche. Escludere il solo foglio
di controllo non dimostra assenza di informazioni future per una valutazione
al 2025. Confermare con G1/G3 data, disponibilita' delle fonti e maturita'.
Le pagine/fonti da verificare e la fragilita' statistica del metodo macro
(campione 9-11 osservazioni) restano quelle dichiarate nel file originale.

Nessuna modifica a WACC, ponte, azioni, margini D10 o stato dei dati G2.
Il run finale blocca D05 provvisorio oltre agli altri blocchi gia' presenti.
La presenza di D05 non risolve l'assenza delle funzioni e dei WACC G3.
