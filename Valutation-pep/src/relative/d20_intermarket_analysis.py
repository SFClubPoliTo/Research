# -*- coding: utf-8 -*-
"""
================================================================================
STARTING FINANCE CLUB POLITO - AREA RESEARCH
PROGETTO VALUATION PEPSICO (PEP) - SEMESTRE AUTUNNALE 2026
--------------------------------------------------------------------------------
DELIVERABLE D20: QUADRO DI SETTORE E INTER-MARKET ANALYSIS (v0)
Autori: Davide & Saverio (Gruppo 5 - Relative Valuation)
Data: 29 ottobre 2026

Descrizione:
Script econometrico unificato per l'analisi inter-market di PepsiCo (PEP).
- Esegue l'analisi su due finestre temporali:
    1. Finestra 5 Anni: 2020-01-01 - 2025-12-31 (Baseline)
    2. Finestra 10 Anni: 2015-01-01 - 2025-12-31 (Robustness & Stability Check)
- Calcola:
    * Test di stazionarietà ADF (Augmented Dickey-Fuller)
    * Matrice di correlazione inter-market e con i peer
    * Regressioni unifattoriali del Beta: PEP vs S&P 500, PEP vs NASDAQ, PEP vs XLP, PEP vs Peers
    * Regressione multifattoriale con Errori HAC Newey-West (maxlags=3)
    * Diagnostica completa (Durbin-Watson, Jarque-Bera, VIF)
    * Esportazione tabelle CSV e grafici ad alta risoluzione
================================================================================
"""

import os
import sys
import numpy as np
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.stattools import durbin_watson, jarque_bera
from statsmodels.stats.outliers_influence import variance_inflation_factor
import matplotlib.pyplot as plt
import seaborn as sns

# Configurazione grafica
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

# Cartella di output
OUTPUT_DIR = "output_d20"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. DEFINIZIONE DEI TICKER
TICKERS_DICT = {
    'PEP': 'PEP',          # Target PepsiCo
    'SPY': 'SPY',          # S&P 500 ETF (Mercato Generale)
    'QQQ': 'QQQ',          # NASDAQ 100 ETF (Mercato Tech/Growth)
    'XLP': 'XLP',          # Consumer Staples Select Sector SPDR (Settore)
    'TNX': '^TNX',         # US 10-Year Treasury Yield (Tassi di interesse)
    'DXY': 'DX-Y.NYB',     # US Dollar Index (FX / Forza del Dollaro)
    'Corn': 'ZC=F',        # Mais Futures (Input snack Frito-Lay)
    'Sugar': 'SB=F',       # Zucchero #11 Futures (Input bevande PBNA)
    'Oil': 'CL=F',         # WTI Crude Oil (Energia, packaging plastica PET, trasporti)
    # Core Peers per paniere equal-weighted
    'KO': 'KO',
    'KDP': 'KDP',
    'MNST': 'MNST',
    'MDLZ': 'MDLZ',
    'HSY': 'HSY'
}

print("=" * 80)
print("STARTING FINANCE CLUB POLITO | G5 - RELATIVE VALUATION")
print("ESECUZIONE ANALISI INTER-MARKET UNIFICATA (DELIVERABLE D20)")
print("=" * 80)

print("\n[1/5] Download serie storiche mensili da Yahoo Finance (2015-2025)...")
tickers_list = list(TICKERS_DICT.values())
raw_data = yf.download(tickers_list, start='2015-01-01', end='2025-12-31', interval='1mo', auto_adjust=True)['Close']

# Riorganizzazione DataFrame con nomi puliti
df_prices = pd.DataFrame(index=raw_data.index)
for clean_name, ticker in TICKERS_DICT.items():
    if ticker in raw_data.columns:
        df_prices[clean_name] = raw_data[ticker]
    else:
        print(f"Attenzione: colonna non trovata per {clean_name} ({ticker})")

df_prices = df_prices.dropna()
print(f"Dati scaricati con successo. Righe totali: {len(df_prices)} mesi.")

# 2. CALCOLO RENDIMENTI LOGARITMICI E PRIME DIFFERENZE
print("\n[2/5] Calcolo rendimenti logaritmici e variazione tassi...")
df_rets = pd.DataFrame(index=df_prices.index[1:])
for col in df_prices.columns:
    if col == 'TNX':
        # Per i tassi usiamo le prime differenze (variazione in punti percentuali / p.p.)
        df_rets['d_TNX'] = df_prices['TNX'].diff().dropna()
    else:
        # Rendimenti logaritmici mensili: r_t = ln(P_t / P_{t-1})
        df_rets[f'r_{col}'] = np.log(df_prices[col] / df_prices[col].shift(1)).dropna()

# Calcolo del rendimento medio del paniere di peer core (Equal-Weighted Peers)
peer_cols = ['r_KO', 'r_KDP', 'r_MNST', 'r_MDLZ', 'r_HSY']
df_rets['r_PEERS_EW'] = df_rets[peer_cols].mean(axis=1)

df_rets = df_rets.dropna()

# 3. FUNZIONE DI ANALISI ECONOMETRICA PER FINESTRA
def run_window_analysis(df_window, window_label):
    print(f"\n" + "-" * 70)
    print(f"ANALISI FINESTRA: {window_label} (N = {len(df_window)} osservazioni mensili)")
    print("-" * 70)

    # A. Test di Stazionarietà ADF
    adf_results = []
    series_to_test = ['r_PEP', 'r_XLP', 'r_SPY', 'r_QQQ', 'd_TNX', 'r_DXY', 'r_Corn', 'r_Sugar', 'r_Oil', 'r_PEERS_EW']
    for s in series_to_test:
        stat, pval, _, _, _, _ = adfuller(df_window[s])
        adf_results.append({
            'Variabile': s,
            'ADF_Stat': round(stat, 4),
            'p_value': round(pval, 4),
            'Stazionario_5pct': pval < 0.05
        })
    df_adf = pd.DataFrame(adf_results)
    
    # B. Matrice di Correlazione
    corr_matrix = df_window[series_to_test].corr().round(3)

    # C. Regressioni Unifattoriali del Beta (CAPM & Benchmarks) con errori HAC
    beta_specs = [
        ('Mercato S&P 500 (SPY)', 'r_SPY'),
        ('Mercato NASDAQ 100 (QQQ)', 'r_QQQ'),
        ('Settore Consumer Staples (XLP)', 'r_XLP'),
        ('Paniere Core Peers (Equal-Weighted)', 'r_PEERS_EW')
    ]
    beta_results = []
    for bench_name, bench_col in beta_specs:
        X = sm.add_constant(df_window[bench_col])
        y = df_window['r_PEP']
        m = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 3})
        beta_val = m.params[bench_col]
        se_val = m.bse[bench_col]
        pval = m.pvalues[bench_col]
        r2 = m.rsquared
        beta_results.append({
            'Benchmark': bench_name,
            'Beta_Stima': round(beta_val, 4),
            'Std_Error_HAC': round(se_val, 4),
            't_stat': round(m.tvalues[bench_col], 3),
            'p_value': round(pval, 4),
            'R_squared': round(r2, 4)
        })
    df_beta = pd.DataFrame(beta_results)

    # D. Regressione Multifattoriale Macro Inter-Market (Errori HAC Newey-West)
    macro_vars = ['r_SPY', 'd_TNX', 'r_DXY', 'r_Corn', 'r_Sugar', 'r_Oil']
    X_macro = sm.add_constant(df_window[macro_vars])
    y_pep = df_window['r_PEP']
    model_hac = sm.OLS(y_pep, X_macro).fit(cov_type='HAC', cov_kwds={'maxlags': 3})
    
    # Diagnostica
    dw_stat = durbin_watson(model_hac.resid)
    jb_stat, jb_pval, _, _ = jarque_bera(model_hac.resid)
    
    # Calcolo VIF
    vif_data = []
    for i, col in enumerate(macro_vars):
        v = variance_inflation_factor(df_window[macro_vars].values, i)
        vif_data.append({'Variabile': col, 'VIF': round(v, 2)})
    df_vif = pd.DataFrame(vif_data)

    # Tabella riepilogativa coefficienti macro
    macro_coefs = []
    expected_signs = {
        'r_SPY': '+ (Beta difensivo < 1)',
        'd_TNX': '- (Rialzo tassi penalizza staples)',
        'r_DXY': '- (Dollaro forte penalizza ricavi esteri)',
        'r_Corn': '- (Aumento costi snack Frito-Lay)',
        'r_Sugar': '- (Aumento costi bevande PBNA)',
        'r_Oil': '-/+ (Costi packaging/trasporti)'
    }
    
    for var in macro_vars:
        c = model_hac.params[var]
        se = model_hac.bse[var]
        pv = model_hac.pvalues[var]
        macro_coefs.append({
            'Variabile': var,
            'Segno_Atteso': expected_signs.get(var, 'N/A'),
            'Coefficiente': round(c, 4),
            'Std_Err_HAC': round(se, 4),
            'p_value': round(pv, 4),
            'Significativo_10pct': pv < 0.10
        })
    df_macro = pd.DataFrame(macro_coefs)

    return {
        'label': window_label,
        'N': len(df_window),
        'adf': df_adf,
        'corr': corr_matrix,
        'beta': df_beta,
        'macro': df_macro,
        'r2': round(model_hac.rsquared, 4),
        'adj_r2': round(model_hac.rsquared_adj, 4),
        'f_stat': round(model_hac.fvalue, 3) if hasattr(model_hac, 'fvalue') else 'N/A',
        'dw': round(dw_stat, 3),
        'jb_pvalue': round(jb_pval, 4),
        'vif': df_vif,
        'model_obj': model_hac
    }

# 4. ESECUZIONE SULLE DUE FINESTRE
res_5y = run_window_analysis(df_rets.loc['2020-01-01':], '5 Anni (2020-2025) - Baseline')
res_10y = run_window_analysis(df_rets.loc['2015-01-01':], '10 Anni (2015-2025) - Robustness Full-Cycle')

# 5. GENERAZIONE REPORT COMPARATIVO A CONSOLLE
print("\n" + "=" * 80)
print("QUADRO COMPARATIVO DEI RISULTATI ECONOMETRICI (PER LA NOTA D20)")
print("=" * 80)

print("\n--- 1. CONFRONTO STABILITÀ DEI BETA BENCHMARK ---")
comp_beta = pd.merge(
    res_5y['beta'][['Benchmark', 'Beta_Stima', 'p_value', 'R_squared']],
    res_10y['beta'][['Benchmark', 'Beta_Stima', 'p_value', 'R_squared']],
    on='Benchmark',
    suffixes=(' [5Y]', ' [10Y]')
)
print(comp_beta.to_string(index=False))

print("\n--- 2. CONFRONTO REGRESSIONE MULTIFATTORIALE MACRO (ERRORI HAC) ---")
comp_macro = pd.merge(
    res_5y['macro'][['Variabile', 'Segno_Atteso', 'Coefficiente', 'p_value']],
    res_10y['macro'][['Variabile', 'Coefficiente', 'p_value']],
    on='Variabile',
    suffixes=(' [5Y]', ' [10Y]')
)
print(comp_macro.to_string(index=False))

print("\n--- 3. DIAGNOSTICA GENERALE DEI MODELLI ---")
print(f"Statistica                | 5 Anni (2020-2025) | 10 Anni (2015-2025)")
print(f"Osservazioni (N)          | {res_5y['N']:18} | {res_10y['N']:19}")
print(f"R-squared                 | {res_5y['r2']:18} | {res_10y['r2']:19}")
print(f"R-squared Corretto (Adj)  | {res_5y['adj_r2']:18} | {res_10y['adj_r2']:19}")
print(f"Durbin-Watson (DW)        | {res_5y['dw']:18} | {res_10y['dw']:19}")
print(f"Jarque-Bera (p-value)     | {res_5y['jb_pvalue']:18} | {res_10y['jb_pvalue']:19}")

print("\n--- 4. MULTICOLLINEARITÀ (VIF) SULLA FINESTRA 5 ANNI ---")
print(res_5y['vif'].to_string(index=False))

# 6. ESPORTAZIONE TABELLE CSV
print(f"\n[4/5] Salvataggio tabelle di deliverable in '{OUTPUT_DIR}'...")
comp_beta.to_csv(os.path.join(OUTPUT_DIR, "D20_confronto_beta_5y_10y.csv"), index=False, sep=";")
comp_macro.to_csv(os.path.join(OUTPUT_DIR, "D20_regressione_macro_hac.csv"), index=False, sep=";")
res_5y['corr'].to_csv(os.path.join(OUTPUT_DIR, "D20_matrice_correlazione_5y.csv"), sep=";")
res_10y['corr'].to_csv(os.path.join(OUTPUT_DIR, "D20_matrice_correlazione_10y.csv"), sep=";")
res_5y['adf'].to_csv(os.path.join(OUTPUT_DIR, "D20_test_stazionarieta_adf.csv"), index=False, sep=";")

# 7. GENERAZIONE GRAFICI AD ALTA RISOLUZIONE
print("\n[5/5] Generazione grafici per il report D20...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Subplot 1: Correlazioni Heatmap 5Y
sns.heatmap(res_5y['corr'].loc[['r_PEP', 'r_XLP'], ['r_SPY', 'r_QQQ', 'd_TNX', 'r_DXY', 'r_Corn', 'r_Sugar', 'r_Oil']], 
            annot=True, fmt=".2f", cmap="vlag", center=0, ax=axes[0, 0], cbar=False)
axes[0, 0].set_title("Matrice Correlazioni Inter-Market (5 Anni: 2020-2025)", fontsize=11, fontweight='bold', color='#1B365D')

# Subplot 2: Confronto Beta per Benchmark (5Y vs 10Y)
b_df = comp_beta.copy()
x_pos = np.arange(len(b_df))
width = 0.35
axes[0, 1].bar(x_pos - width/2, b_df['Beta_Stima [5Y]'], width, label='5 Anni (2020-2025)', color='#1B365D')
axes[0, 1].bar(x_pos + width/2, b_df['Beta_Stima [10Y]'], width, label='10 Anni (2015-2025)', color='#4A607A')
axes[0, 1].set_xticks(x_pos)
axes[0, 1].set_xticklabels(['S&P 500', 'NASDAQ 100', 'XLP (Staples)', 'Peers EW'], fontsize=9)
axes[0, 1].set_ylabel("Beta Stimato (HAC)")
axes[0, 1].set_title("Stabilità Strutturale del Beta su Differenti Orizzonti", fontsize=11, fontweight='bold', color='#1B365D')
axes[0, 1].legend(frameon=True)
axes[0, 1].axhline(1.0, color='red', linestyle='--', linewidth=0.8, alpha=0.7, label='Mercato (1.0)')

# Subplot 3: Rendimenti cumulati normalizzati PEP vs SPY vs QQQ vs XLP (2020-2025)
cum_rets = (1 + df_rets.loc['2020-01-01':, ['r_PEP', 'r_SPY', 'r_QQQ', 'r_XLP']]).cumprod()
axes[1, 0].plot(cum_rets.index, cum_rets['r_PEP'], label='PEP (PepsiCo)', color='#1B365D', linewidth=2)
axes[1, 0].plot(cum_rets.index, cum_rets['r_XLP'], label='XLP (Staples ETF)', color='#2B7A78', linewidth=1.5, linestyle='-.')
axes[1, 0].plot(cum_rets.index, cum_rets['r_SPY'], label='SPY (S&P 500)', color='#D9534F', linewidth=1.2, linestyle='--')
axes[1, 0].plot(cum_rets.index, cum_rets['r_QQQ'], label='QQQ (NASDAQ 100)', color='#F0AD4E', linewidth=1.2, linestyle=':')
axes[1, 0].set_title("Dinamica Rendimenti Cumulati: Rotazione Difensiva", fontsize=11, fontweight='bold', color='#1B365D')
axes[1, 0].set_ylabel("Rendimento Cumulato (Base 1)")
axes[1, 0].legend(frameon=True, fontsize=8)

# Subplot 4: Residui della regressione HAC (5Y)
resids_5y = res_5y['model_obj'].resid
axes[1, 1].plot(resids_5y.index, resids_5y, color='#1B365D', linewidth=1.2, marker='o', markersize=3)
axes[1, 1].axhline(0, color='black', linestyle='--', linewidth=0.8)
axes[1, 1].axhline(2*np.std(resids_5y), color='red', linestyle=':', linewidth=0.8, label='+/- 2 Std Dev')
axes[1, 1].axhline(-2*np.std(resids_5y), color='red', linestyle=':', linewidth=0.8)
axes[1, 1].set_title("Residui Regressione Multifattoriale HAC (Newey-West)", fontsize=11, fontweight='bold', color='#1B365D')
axes[1, 1].set_ylabel("Residuo OLS")
axes[1, 1].legend(frameon=True, fontsize=8)

plt.tight_layout()
chart_path = os.path.join(OUTPUT_DIR, "D20_grafici_intermarket.png")
plt.savefig(chart_path, dpi=300)
plt.close()

print(f"Grafico salvato in: {chart_path}")
print("\n" + "=" * 80)
print("ANALISI D20 COMPLETATA CON SUCCESSO! I FILE SONO PRONTI PER LA NOTA FORMALE.")
print("=" * 80)
