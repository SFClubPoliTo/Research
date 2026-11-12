import yfinance as yf
import pandas as pd
from scipy.stats import linregress
'''
    Beta
    G5: agree with the group on the method for Beta
    Now: Read CSV file of D09 from G5 (v1) and calculate Beta bottom-up, with Blume on the raw betas.
    Also: beta linear regression on a single ticker, as a check
    D09: separator ';', comment lines starting with '#', one row per company
    D09 columns used: tier, market_cap_usd_bn, total_debt_usd_bn, operating_leases_usd_bn, beta_observed
    Debt = total debt WITHOUT operating leases (as for PepsiCo, D03)
'''
def calculate_beta_regression(ticker, benchmark='^GSPC', start='2021-01-01', end='2026-01-01'):
    data_ticker = yf.download(ticker, start=start, end=end, interval='1mo')['Close']
    data_bench = yf.download(benchmark, start=start, end=end, interval='1mo')['Close']

    df = pd.concat([data_ticker, data_bench], axis=1).dropna()
    df.columns = [ticker, benchmark]

    yields = df.pct_change().dropna()
    slope, _, _, _, _ = linregress(yields[benchmark], yields[ticker])

    return float(slope.iloc[0]) if isinstance(slope, pd.Series) else slope

def calculate_beta_bottom_up(file_csv_G5, tax_rate_pep, d_e_ratio_pep):
    df_peers = pd.read_csv(file_csv_G5, sep=';', comment='#')
    df_peers = df_peers[df_peers['tier'] == 'Tier 1'].copy() # the 9 core peers (G1, D06)
    df_peers['debt'] = df_peers['total_debt_usd_bn'] - df_peers['operating_leases_usd_bn']
    df_peers['D_E_ratio'] = df_peers['debt'] / df_peers['market_cap_usd_bn']
    # Blume on the raw beta, before unlevering
    df_peers['beta_blume'] = 0.67 * df_peers['beta_observed'] + 0.33
    # Unlevering: Beta_U = Beta_L / [1 + (1- Tax)*(D/E)], same tax rate for all the peers
    df_peers['beta_unlevered'] = df_peers['beta_blume']/ (1+(1-tax_rate_pep)* df_peers['D_E_ratio'])

    median_beta_u = df_peers['beta_unlevered'].median()
    # Relevering: Beta_L_PEP = Beta_U_Mediana * [1 + (1 - Tax_PEP) * (D/E_PEP)]
    beta_levered_pep = median_beta_u * (1 + (1 - tax_rate_pep) * d_e_ratio_pep)

    return beta_levered_pep, median_beta_u, df_peers


if __name__ =="__main__":
    # Test of the linear regression
    beta_test_ko = calculate_beta_regression('KO')
    print(f'Beta observed of the test for Coca_Cola: {beta_test_ko:.3f}')

    # D09 from G5, run from codice/ (expected: median Beta_U 0.4142, Beta of PepsiCo 0.5110)
    tax_pep = 0.21 # H10
    d_e_pep = 51.881 / (128.34 * 1.366) # D13: debt 10-Q p. 6, leases excluded / price 2026-10-08 x diluted shares
    beta_pepsico, med_u, df = calculate_beta_bottom_up('../dati/D09_peer_beta_v1_G5.csv', tax_pep, d_e_pep)
    print(f'Median Beta_U of the peers: {med_u:.4f}')
    print(f'Beta of PepsiCo: {beta_pepsico:.4f}')
