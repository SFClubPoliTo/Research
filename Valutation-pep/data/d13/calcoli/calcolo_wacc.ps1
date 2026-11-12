# =====================================================================
# G3 - Calcolo del WACC (D13 v2)
# Esegui da PowerShell:  .\calcoli\calcolo_wacc.ps1   (dalla cartella G3)
# Legge:  dati\D09_peer_beta_v1_G5.csv (G5, D09 v1)
# Scrive: consegne\D13_tassi_v2_G3.csv, consegne\D13_wacc_annuale_v2_G3.csv, consegne\D13_beta_peer_v2_G3.csv e consegne\D13_config_v2_G3.yaml
# Data di valutazione (H01): 8/10/2026, giorno in cui escono 10-Q e risultati (accettati dalla SEC il 7/10 dopo la chiusura); dati di mercato all'8/10.
# Bilancio del ponte al 5/9/2026 (10-Q): i flussi si contano dal 6/9, lo sconto parte dall'8/10 (G2).
# Stato: definitivo. Beta bottom-up sui 9 peer principali (D09 di G5) con la correzione di Blume.
# Tassi in decimali, importi in miliardi di USD.
# =====================================================================

# Punto decimale nei CSV (il sistema e' in italiano e userebbe la virgola)
[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture

# ---- Input (valore, data, fonte) -------------------------------------
$rf      = 0.0522   # Treasury USA 10 anni nominale, 8/10/2026, LSEG TCM10 (risk_free.xlsx; stessa serie di FRED DGS10)
$erp     = 0.0420   # ERP implicito USA, 1/10/2026, Damodaran ERPbymonth.xlsx (T12m sustainable payout)
$tau     = 0.21     # aliquota federale USA, 10-K p. 78; costante in tutti gli anni (G2)
$price   = 128.34   # prezzo PEP, chiusura 8/10/2026, Yahoo Finance
$stub    = 112 / 364  # quota del FCFF 2026 dopo il bilancio del 10-Q: 6/9-26/12/2026, 112 giorni su 364 dell'anno fiscale
$firstT  = 79 / 364   # distanza del primo flusso dalla data di valutazione: 8/10-26/12/2026, 79 giorni
$shares  = 1.366    # azioni diluite (mld), 10-Q copertina + p. 26
$debt    = 51.881   # debito finanziario (mld), valore contabile al 5/9/2026, 10-Q p. 6; niente leasing (nei flussi, D03)
$ebit    = 11.498   # utile operativo 2025, 10-K p. 57
$intexp  = 1.840    # interessi passivi 2025, 10-K p. 51
$blumeA  = 0.67     # correzione di Blume: 0,67 x beta + 0,33, sui beta grezzi dei peer (G5, D09)
$blumeB  = 0.33
$betaInf = 0.55    # IPOTESI: beta levered a maturita', media del beta a 60 mesi 2016-01/2026-09: PEP 0,557, mediana peer 0,539 (calcoli\beta_storico.ps1)
$k       = 0.5      # convergenza negli anni di transizione (formula ricorsiva, paper su Arm, App. B)
$nGrowth = 5        # anni di crescita (G2)
$nTrans  = 5        # anni di transizione (G2); maturita' dall'anno 11

# ---- Rating sintetico (Damodaran, imprese grandi non finanziarie, gennaio 2026) ----
$table = @(
  @{lo=8.5;  rating='Aaa/AAA'; spread=0.0040},
  @{lo=6.5;  rating='Aa2/AA';  spread=0.0055},
  @{lo=5.5;  rating='A1/A+';   spread=0.0070},
  @{lo=4.25; rating='A2/A';    spread=0.0078},
  @{lo=3.0;  rating='A3/A-';   spread=0.0089},
  @{lo=2.5;  rating='Baa2/BBB';spread=0.0111},
  @{lo=2.25; rating='Ba1/BB+'; spread=0.0138},
  @{lo=2.0;  rating='Ba2/BB';  spread=0.0184}
)
$coverage = $ebit / $intexp
$row = $table | Where-Object { $coverage -gt $_.lo } | Select-Object -First 1
$spread = $row.spread
$rd = $rf + $spread

# ---- Pesi a valori di mercato ----------------------------------------
$E = $price * $shares
$wD = $debt / ($debt + $E)
$wE = 1 - $wD
$DE = $debt / $E

# ---- Beta, costo dell'equity, WACC per stadio --------------------------
# Peer Tier 1 (G1, D06): Blume sul beta grezzo, poi via il debito con Hamada; debito senza leasing operativi, come per PEP (D03)
# Attenzione: PowerShell non distingue maiuscole e minuscole, quindi qui niente $de o $e
$root = Split-Path $PSScriptRoot -Parent
$peers = Get-Content (Join-Path $root 'dati\D09_peer_beta_v1_G5.csv') -Encoding UTF8 | Where-Object { $_ -notmatch '^#' } | ConvertFrom-Csv -Delimiter ';' | Where-Object { $_.tier -eq 'Tier 1' }
$peerBeta = foreach ($p in $peers) {
  $peerDE = ([double]$p.total_debt_usd_bn - [double]$p.operating_leases_usd_bn) / [double]$p.market_cap_usd_bn
  $blume  = $blumeA * [double]$p.beta_observed + $blumeB
  [pscustomobject]@{ ticker = $p.ticker; debt_to_equity = [math]::Round($peerDE, 4); beta_observed = [double]$p.beta_observed; beta_blume = [math]::Round($blume, 4); beta_unlevered = $blume / (1 + (1 - $tau) * $peerDE); beta_unlevered_raw = [double]$p.beta_observed / (1 + (1 - $tau) * $peerDE) }
}
function Get-Median($values) {
  $sorted = @($values | Sort-Object)
  $mid = [math]::Floor($sorted.Count / 2)
  if ($sorted.Count % 2) { return $sorted[$mid] }
  return ($sorted[$mid - 1] + $sorted[$mid]) / 2
}
$betaU = Get-Median ($peerBeta | ForEach-Object { $_.beta_unlevered })
$betaG = $betaU * (1 + (1 - $tau) * $DE)
$reG   = $rf + $betaG * $erp
$reInf = $rf + $betaInf * $erp
$rdAT  = $rd * (1 - $tau)
$wG    = $wE * $reG + $wD * $rdAT
$wInf  = $wE * $reInf + $wD * $rdAT
# Controllo: stesso calcolo sui beta grezzi, senza Blume (citato nella sezione LaTeX)
$betaRaw = (Get-Median ($peerBeta | ForEach-Object { $_.beta_unlevered_raw })) * (1 + (1 - $tau) * $DE)
$reRaw   = $rf + $betaRaw * $erp
$wRaw    = $wE * $reRaw + $wD * $rdAT

# ---- Percorso annuale: anni 1-5 crescita, 6-10 transizione, 11 maturita' ----
# Anno 1 = esercizio 2026, di cui conta solo la parte dopo il bilancio del 10-Q; flussi a fine anno fiscale, scontati dall'8/10
$H = $nGrowth + $nTrans
$path = @()
$w = $wG
for ($t = 1; $t -le $H + 1; $t++) {
  if ($t -le $nGrowth) { $w = $wG; $stage = 'growth' }
  elseif ($t -le $H) { $w = $w + $k * ($wInf - $w); $stage = 'transition' }
  else { $w = $wInf; $stage = 'maturity' }
  # Niente arrotondamenti: con sigma = 0 la pipeline deve ritrovare il DCF deterministico (G2)
  $time = if ($t -le $H) { $firstT + ($t - 1) } else { '' }
  $path += [pscustomobject]@{ year = $t; fiscal_year = 2025 + $t; stage = $stage; wacc = $w; discount_time = $time }
}

# ---- Output --------------------------------------------------------------
$out = Join-Path $root 'consegne'
# UTF-8 senza BOM, cosi' pandas e PyYAML leggono la prima riga senza sorprese
function Set-Content { param($Path, $Value, $Encoding) [System.IO.File]::WriteAllText($Path, ($Value -join "`n") + "`n", (New-Object System.Text.UTF8Encoding($false))) }
$header = "# D13 tassi e WACC - G3 -> G4 - v2 - generato $(Get-Date -Format 'yyyy-MM-dd') - data di valutazione 2026-10-08 - stato: definitivo`n# Tassi in decimali; importi in miliardi di USD"
$params = @(
  [pscustomobject]@{parametro='valuation_date'; valore='2026-10-08'; data=''; fonte='H01: uscita di 10-Q e risultati (accettati dalla SEC il 7/10 dopo la chiusura)'; stato='reale'},
  [pscustomobject]@{parametro='balance_sheet_date'; valore='2026-09-05'; data=''; fonte='10-Q terzo trimestre 2026'; stato='reale'},
  [pscustomobject]@{parametro='first_year_fraction'; valore=$stub.ToString('R'); data=''; fonte='112/364: quota del FCFF 2026 contata (6/9-26/12/2026)'; stato='reale'},
  [pscustomobject]@{parametro='first_discount_period'; valore=$firstT.ToString('R'); data=''; fonte='79/364: distanza del primo flusso (8/10-26/12/2026)'; stato='reale'},
  [pscustomobject]@{parametro='rf'; valore=$rf; data='2026-10-08'; fonte='LSEG TCM10 (= FRED DGS10)'; stato='reale'},
  [pscustomobject]@{parametro='erp'; valore=$erp; data='2026-10-01'; fonte='Damodaran ERPbymonth.xlsx, T12m sustainable payout'; stato='reale'},
  [pscustomobject]@{parametro='beta_unlevered'; valore=[math]::Round($betaU,4); data='2025-12-31'; fonte='G5 D09 v1: mediana dei 9 peer Tier 1 (G1 D06), Blume e Hamada al 21%, debito senza leasing operativi'; stato='reale'},
  [pscustomobject]@{parametro='beta_levered_growth'; valore=[math]::Round($betaG,4); data=''; fonte='beta_unlevered con il D/E di PEP'; stato='reale'},
  [pscustomobject]@{parametro='beta_levered_maturity'; valore=$betaInf; data='2016-01/2026-09'; fonte='ipotesi G3: media del beta a 60 mesi (dati/beta_storico_60m.csv)'; stato='reale'},
  [pscustomobject]@{parametro='interest_coverage'; valore=[math]::Round($coverage,3); data='2025'; fonte='10-K p. 57 e p. 51'; stato='reale'},
  [pscustomobject]@{parametro='synthetic_rating'; valore=$row.rating; data='2026-01'; fonte='Damodaran ratings.html'; stato='reale'},
  [pscustomobject]@{parametro='default_spread'; valore=$spread; data='2026-01'; fonte='Damodaran ratings.html'; stato='reale'},
  [pscustomobject]@{parametro='rd_pretax'; valore=[math]::Round($rd,5); data=''; fonte='rf + spread'; stato='reale'},
  [pscustomobject]@{parametro='tax_marginal'; valore=$tau; data=''; fonte='10-K p. 78'; stato='reale'},
  [pscustomobject]@{parametro='price'; valore=$price; data='2026-10-08'; fonte='Yahoo Finance, chiusura'; stato='reale'},
  [pscustomobject]@{parametro='diluted_shares_bn'; valore=$shares; data='2026-10-01'; fonte='10-Q copertina e p. 26, treasury stock method (H12)'; stato='reale'},
  [pscustomobject]@{parametro='equity_market_value_bn'; valore=[math]::Round($E,3); data='2026-10-08'; fonte='calcolato'; stato='reale'},
  [pscustomobject]@{parametro='debt_bn'; valore=$debt; data='2026-09-05'; fonte='10-Q p. 6 (valore contabile)'; stato='reale'},
  [pscustomobject]@{parametro='debt_weight'; valore=[math]::Round($wD,4); data=''; fonte='calcolato'; stato='reale'},
  [pscustomobject]@{parametro='cost_of_equity_growth'; valore=[math]::Round($reG,5); data=''; fonte='CAPM'; stato='reale'},
  [pscustomobject]@{parametro='cost_of_equity_maturity'; valore=[math]::Round($reInf,5); data=''; fonte='CAPM'; stato='reale'},
  [pscustomobject]@{parametro='wacc_growth'; valore=[math]::Round($wG,5); data=''; fonte='calcolato'; stato='reale'},
  [pscustomobject]@{parametro='wacc_maturity'; valore=[math]::Round($wInf,5); data=''; fonte='calcolato'; stato='reale'},
  [pscustomobject]@{parametro='k_transition'; valore=$k; data=''; fonte='paper su Arm, App. B; stesso k di ricavi e margini (G1 D10)'; stato='reale'},
  [pscustomobject]@{parametro='years_growth'; valore=$nGrowth; data=''; fonte='G2'; stato='reale'},
  [pscustomobject]@{parametro='years_transition'; valore=$nTrans; data=''; fonte='G2'; stato='reale'}
)
$peerOut = $peerBeta | Select-Object ticker, debt_to_equity, beta_observed, beta_blume, @{ Name = 'beta_unlevered'; Expression = { [math]::Round($_.beta_unlevered, 4) } }, @{ Name = 'beta_unlevered_raw'; Expression = { [math]::Round($_.beta_unlevered_raw, 4) } }
Set-Content -Path (Join-Path $out 'D13_tassi_v2_G3.csv') -Value ($header + "`n" + (($params | ConvertTo-Csv -NoTypeInformation) -join "`n")) -Encoding utf8
Set-Content -Path (Join-Path $out 'D13_wacc_annuale_v2_G3.csv') -Value ($header + "`n" + (($path | ConvertTo-Csv -NoTypeInformation) -join "`n")) -Encoding utf8
Set-Content -Path (Join-Path $out 'D13_beta_peer_v2_G3.csv') -Value ($header + "`n" + (($peerOut | ConvertTo-Csv -NoTypeInformation) -join "`n")) -Encoding utf8

# Blocco per il file di configurazione di G4 (anni 1..H nel vettore; wacc_maturity per il terminale)
$vec = ($path | Where-Object { $_.year -le $H } | ForEach-Object { $_.wacc.ToString('R') }) -join ', '
$times = ($path | Where-Object { $_.year -le $H } | ForEach-Object { $_.discount_time.ToString('R') }) -join ', '
$yaml = @"
# D13 - G3 -> G4 - v2 - generato $(Get-Date -Format 'yyyy-MM-dd') - definitivo
# Tassi in decimali, annuali, nominali, USD. Il WACC e' deterministico: uguale in tutti i percorsi e in tutti gli scenari.
rates:
  status: definitivo
  valuation_date: 2026-10-08    # H01: uscita di 10-Q e risultati; bilancio del ponte al 2026-09-05
  first_year_fraction: $($stub.ToString('R'))   # = 112/364: del FCFF 2026 conta solo questa quota (6/9-26/12/2026, dopo il bilancio)
  first_discount_period: $($firstT.ToString('R'))   # = 79/364: anni dalla data di valutazione alla fine dell'esercizio 2026 (8/10-26/12)
  discount_time: [$times]   # anni dalla data di valutazione, flussi a fine esercizio 2026..$(2025 + $H); il terminal value usa l'ultimo
  rf: $rf                       # LSEG TCM10 (= FRED DGS10), 2026-10-08
  erp: $erp                     # Damodaran ERPbymonth, 2026-10-01
  beta_levered_growth: $([math]::Round($betaG,4))   # G5 D09 v1: mediana dei 9 peer con Blume, D/E di PEP
  beta_levered_maturity: $betaInf  # ipotesi G3: media del beta a 60 mesi, 2016-2026
  rd_pretax: $([math]::Round($rd,5))            # rf + spread rating sintetico A+ (Damodaran)
  tax_marginal: $tau             # H10: 21% nel WACC e nel NOPAT a regime; il NOPAT parte dal 19% e converge negli anni 6-10 (G2)
  debt_weight: $([math]::Round($wD,4))           # D/(D+E), D al 2026-09-05, E al 2026-10-08
  years_growth: $nGrowth
  years_transition: $nTrans
  k_transition: $k
  wacc_growth: $($wG.ToString('R'))
  wacc_maturity: $($wInf.ToString('R'))       # w_inf: usato nel terminal value
  wacc_by_year: [$vec]   # anni 1..$H = esercizi 2026..$(2025 + $H)
"@
Set-Content -Path (Join-Path $out 'D13_config_v2_G3.yaml') -Value $yaml -Encoding utf8

$peerOut | Format-Table -AutoSize | Out-String -Width 200
$params | Format-Table -AutoSize | Out-String -Width 200
$path | Format-Table -AutoSize | Out-String -Width 200
"Controllo senza Blume: beta {0:N4}, r_e {1:N5}, r_e - r_d {2:N5}, WACC crescita {3:N5}" -f $betaRaw, $reRaw, ($reRaw - $rd), $wRaw
