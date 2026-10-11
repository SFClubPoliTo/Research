# Verifica delle misure: oro e rame - 5 ottobre 2026

La pipeline prezzi e la mappatura operativa sono comuni ai due metalli. Il problema della misura riguarda entrambi; lo storico di IV non stima automaticamente premi fisici.

## Esito

- Calibrazione opzioni: Q con tassi deterministici, dopo approssimazione American-equivalent per HXE. La normalizzazione prezzo/forward/discount non cambia la misura in P.
- Simulazione corporate: legge artificiale R, coefficienti option-implied trasferiti ad ancore/scenari e WACC campionato indipendentemente. Nessuna densita Radon-Nikodym, premio di rischio fisico o pricing kernel stimato.
- Rame: la curva F(0,T) tra delivery differenti impone una media; non e il drift nel tempo di un future a delivery fisso. Per quest'ultimo, nella convenzione usata, drift zero e premio opzioni scontato al tasso risk-free.
- Oro: ancorare coefficienti GLD a oro realizzato USD/oz non conserva una legge Q di oro negoziabile. Nessuna conversione GLD/oz o carry/convenience-yield stimata.
- Salti: compensatore lambda*(E[exp(J)]-1), con intensity e mark-law simulati; nel passo Hawkes intensity a inizio intervallo. Sotto un'altra misura intensity e mark-law possono cambiare insieme al drift. Cambiare solo drift non identifica P.
- WACC non e short rate. Q-shaped cash flows + WACC possono mescolare aggiustamenti di rischio incompatibili. Sostituire WACC con risk-free da solo non riconcilia un claim corporate incompleto.

## Verifica eseguibile

Il modulo measure_contract distingue pricing Q e scenario R e rifiuta leggi P/Q corporate non implementate. Il manifest esporta i limiti. Cinque nuovi test verificano rifiuto delle misure e media dei quattro simulatori a drift zero con momenti di salto non nulli; il confronto con schedule 12% verifica che il prezzo venga solo moltiplicato per exp(0.12), non trasformato in P. Paper: 22 test passati. Il replay 20261005-paper-measure-audit conserva esattamente summary, quantili e diagnostics del 3 ottobre.

I modelli operativi del rame restano una proiezione controllata di vendite/CoS Q2 fissi, non una replica dei forecast SARIMA mine-level dell'oro. I modelli di prezzo e i test temporali sono applicati a entrambi.

## Priorita economiche ancora aperte

Per un DCF fisico occorre stimare una legge P con prezzi/returns spot o futures coerenti, basis realizzato, premi di prezzo/varianza e tilt dei salti, dipendenza con operations e un discount contract compatibile. Per pricing Q occorre invece una struttura commodity coerente (carry/convenience yield e curva), pricing kernel/numeraire e trattamento dei rischi corporate non spanning. I parametri Hawkes Q non provano news clustering P. Nessuna scelta di premio e inventata dal solo campione OOS.

Fonti: [Schwartz (1997)](https://doi.org/10.1111/j.1540-6261.1997.tb02721.x), [Damodaran: valuation](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/background/valintro.htm), [Geman: numeraire e futures](https://booksite.elsevier.com/samplechapters/9780120476824/9780120476824.PDF). Le conclusioni sul codice sono verifiche della nostra implementazione, non risultati empirici di queste fonti.
