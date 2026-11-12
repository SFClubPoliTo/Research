# =====================================================================
# G3 - Andamento del beta a 60 mesi, base del beta di maturita'
# Esegui da PowerShell:  .\calcoli\beta_storico.ps1   (dalla cartella G3)
# Scrive: dati\beta_storico_60m.csv
# Prezzi: chiusure mensili rettificate, Yahoo Finance, come D09 di G5; mercato: S&P 500 (^GSPC).
# Controllo: sulla finestra 2021-01 / 2025-12 riproduce i beta osservati di D09.
# =====================================================================

# Punto decimale nei CSV (il sistema e' in italiano e userebbe la virgola)
[System.Threading.Thread]::CurrentThread.CurrentCulture = [System.Globalization.CultureInfo]::InvariantCulture
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$firstEnd = '2016-01'   # prima finestra: 2011-02 / 2016-01
$lastEnd  = '2026-09'   # ultimo mese completo prima della data di valutazione (8/10/2026, H01)
$nMonths  = 60
$peers = @('KO','KDP','MNST','MDLZ','HSY','GIS','KHC','HRL','CPB')   # peer Tier 1 (G1, D06)

$p1 = [DateTimeOffset]::new(2010,1,1,0,0,0,[TimeSpan]::Zero).ToUnixTimeSeconds()
$p2 = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

function Get-Returns($ticker) {
  $url = "https://query1.finance.yahoo.com/v8/finance/chart/$([uri]::EscapeDataString($ticker))?period1=$p1&period2=$p2&interval=1mo&includeAdjustedClose=true"
  $res = (Invoke-RestMethod -Uri $url -UserAgent 'Mozilla/5.0' -TimeoutSec 60).chart.result[0]
  $ts = $res.timestamp; $px = $res.indicators.adjclose[0].adjclose
  $prices = [ordered]@{}
  for ($i = 0; $i -lt $ts.Count; $i++) {
    if ($null -eq $px[$i]) { continue }
    $month = [DateTimeOffset]::FromUnixTimeSeconds([long]$ts[$i]).UtcDateTime.AddHours(12).ToString('yyyy-MM')
    if (-not $prices.Contains($month)) { $prices[$month] = [double]$px[$i] }
  }
  $returns = @{}; $keys = @($prices.Keys)
  for ($i = 1; $i -lt $keys.Count; $i++) { $returns[$keys[$i]] = $prices[$keys[$i]] / $prices[$keys[$i-1]] - 1 }
  return $returns
}

function Get-Window($endMonth, $n) {
  $end = [datetime]::ParseExact($endMonth + '-01', 'yyyy-MM-dd', $null)
  $window = @(); for ($i = $n - 1; $i -ge 0; $i--) { $window += $end.AddMonths(-$i).ToString('yyyy-MM') }
  return $window
}

# Pendenza OLS; vuoto se il titolo non copre tutta la finestra (KHC solo dal 2015)
function Get-Beta($rStock, $rMarket, $window) {
  $x = @(); $y = @()
  foreach ($m in $window) {
    if (-not ($rStock.ContainsKey($m) -and $rMarket.ContainsKey($m))) { return $null }
    $x += $rMarket[$m]; $y += $rStock[$m]
  }
  $mx = ($x | Measure-Object -Average).Average; $my = ($y | Measure-Object -Average).Average
  $sxy = 0.0; $sxx = 0.0
  for ($i = 0; $i -lt $x.Count; $i++) { $sxy += ($x[$i] - $mx) * ($y[$i] - $my); $sxx += ($x[$i] - $mx) * ($x[$i] - $mx) }
  return $sxy / $sxx
}

function Get-Median($values) {
  $sorted = @($values | Sort-Object)
  $mid = [math]::Floor($sorted.Count / 2)
  if ($sorted.Count % 2) { return $sorted[$mid] }
  return ($sorted[$mid - 1] + $sorted[$mid]) / 2
}

$ret = @{}
foreach ($t in @('^GSPC','PEP') + $peers) { $ret[$t] = Get-Returns $t; Start-Sleep -Milliseconds 400 }
$rM = $ret['^GSPC']

# ---- Beta di ogni mese ---------------------------------------------------
$rows = @()
$month = [datetime]::ParseExact($firstEnd + '-01', 'yyyy-MM-dd', $null)
$stop  = [datetime]::ParseExact($lastEnd + '-01', 'yyyy-MM-dd', $null)
while ($month -le $stop) {
  $key = $month.ToString('yyyy-MM')
  $window = Get-Window $key $nMonths
  $peerBetas = @(foreach ($t in $peers) { $b = Get-Beta $ret[$t] $rM $window; if ($null -ne $b) { $b } })
  $rows += [pscustomobject]@{ fine_finestra = $key; beta_pep = [math]::Round((Get-Beta $ret['PEP'] $rM $window), 4); beta_mediana_peer = [math]::Round((Get-Median $peerBetas), 4); n_peer = $peerBetas.Count }
  $month = $month.AddMonths(1)
}

# ---- Output --------------------------------------------------------------
$root = Split-Path $PSScriptRoot -Parent
$header = "# Beta a $nMonths mesi di PEP e mediana dei peer Tier 1 - G3 - generato $(Get-Date -Format 'yyyy-MM-dd') - rendimenti mensili, Yahoo Finance, contro S&P 500 (^GSPC); beta grezzi, senza Blume"
$text = $header + "`n" + (($rows | ConvertTo-Csv -NoTypeInformation) -join "`n") + "`n"
[System.IO.File]::WriteAllText((Join-Path $root 'dati\beta_storico_60m.csv'), $text, (New-Object System.Text.UTF8Encoding($false)))

$check = Get-Window '2025-12' $nMonths
"Controllo con D09, finestra 2021-01 / 2025-12:"
foreach ($t in @('PEP') + $peers) { "  {0,-5} {1:N3}" -f $t, (Get-Beta $ret[$t] $rM $check) }
foreach ($col in @('beta_pep','beta_mediana_peer')) {
  $s = $rows | Measure-Object -Property $col -Average -Minimum -Maximum
  $above = @($rows | Where-Object { $_.$col -gt 0.8 }).Count
  "{0}: media {1:N3}, minimo {2:N3}, massimo {3:N3}, mesi sopra 0,80: {4} su {5}" -f $col, $s.Average, $s.Minimum, $s.Maximum, $above, $rows.Count
}
