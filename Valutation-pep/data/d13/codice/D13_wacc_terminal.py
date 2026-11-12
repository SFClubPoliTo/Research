
'''
Module: WACC, Terminal Value, and Enterprise Value (G3)

    This module provides the core valuation engines for the PEP DCF model.
    It is divided into two main classes to facilitate Monte Carlo integration:

    1. WaccCalculator (D13): 
    - Calculates the base WACC.
    - Generates the 3-stage WACC convergence vector over 10 years.

    2. ValueCalculator (D15 preview):
    - Valuation date 2026-10-08 (H01), balance sheet of the bridge at 2026-09-05:
      the part of 2026 after the balance sheet counts (first_year_fraction),
      discounted from the valuation date (first_discount_period).
    - Computes dynamic NOPAT for year H+1 (requires R_H in USD bn).
    - Estimates Terminal Value (TV) via the value driver model.
    - Computes Operating Enterprise Value (EV) bridging FCFF flows from G2.
    - Enforces strict theoretical constraints (ROIC > 0, WACC > g, ROIC >= WACC).
'''

class WaccCalculator:
    def __init__(self, price_share, beta, tax):
        # Values at the valuation date 2026-10-08: same as D13 v2 (consegne/D13_config_v2_G3.yaml)
        self.rf = 0.0522               # G3: 10-year Treasury, LSEG TCM10 (= FRED DGS10), 2026-10-08
        self.beta = beta               # G3: from beta_calculator.py, with the peer data of G5 (D09)
        self.erp = 0.042               # G3: implied ERP, Damodaran, 2026-10-01
        self.rd = 0.0592               # G3: Debt cost pre-tax, rf + spread of synthetic rating A+
        self.tax = tax                 # G3: marginal rate for the debt tax shield (G2 uses 19% for NOPAT)
        self.diluted_shares = 1.366
        self.debt_total = 9.223 + 42.658
        self.price_share = price_share
        self.k_transition = 0.5 

    def calculate_wacc_base(self):
        #  Calculating WACC for one stage
        D = self.debt_total
        E = self.price_share * self.diluted_shares
        re = self.rf + (self.beta * self.erp)
        wacc = (E * re + D * self.rd * (1 - self.tax))/(D + E)
        return wacc


    def generate_wacc_vector(self, wacc_growth, wacc_maturity):
        # Vector WACC for 10 years
        wacc_vector = []

        # Years 1-5: Growth
        for _ in range(5):
            wacc_vector.append(wacc_growth)

        # Years 6-10: Transition
        w_current = wacc_growth
        for _ in range(5):
            w_current += self.k_transition * (wacc_maturity - w_current)
            wacc_vector.append(w_current)

        return wacc_vector


class ValueCalculator:
    def __init__(self, g_inf, tax, first_year_fraction, first_discount_period):
        # self.nopat_h1 = nopat_h1
        self.g_inf = g_inf
        self.tax = tax                                  # G2: NOPAT rate at maturity (21%, reached at the end of the transition)
        self.first_year_fraction = first_year_fraction  # share of FCFF 2026 after the balance sheet (2026-09-05)
        self.first_discount_period = first_discount_period  # years from the valuation date to the end of fiscal 2026

    def calculate_nopat_h1(self, r_h, m_inf):
        # NOPAT_H1 = R_h * (1+ g_inf)* m_inf * (1 - tax)
        nopat_h1 = r_h * (1 + self.g_inf) * m_inf * (1 - self.tax)
        return nopat_h1
    
    def calculate_terminal_value(self, nopat_h1, w_inf, ROIC_inf):
        # TV with value driver formula
        if w_inf <= self.g_inf:   # Check w_inf > g_inf
            raise ValueError ("maturity WACC must be > g_inf")
        if ROIC_inf <= 0:         # Check ROIC_inf > 0
            raise ValueError ("terminal ROIC must be strictly positive")
        if ROIC_inf < w_inf:      # Check ROIC_inf >= w_inf
            raise ValueError ("terminal ROIC must not be lower than the maturity WACC")
        reinvestment_rate = self.g_inf / ROIC_inf
        TV = nopat_h1 * (1 - reinvestment_rate)/(w_inf - self.g_inf)
        return TV
    
    def calculate_discount_factors(self, wacc_vector):
        # No rounding: with sigma = 0 the run must match the deterministic DCF
        # Year-end flows: the first is first_discount_period years away, then one year each (0.22, 1.22, ...)
        df_vector = []
        df_cumulate = 1.0
        for i, wacc_year in enumerate(wacc_vector):
            period = self.first_discount_period if i == 0 else 1.0
            df_cumulate = df_cumulate * (1 + wacc_year) ** (-period)
            df_vector.append(df_cumulate)
        return df_vector

    def calculate_enterprise_value(self, TV, df_vector, fcff_vector):
        # One path at a time: fcff_vector has the 10 yearly FCFF of G2 (full fiscal years 2026-2035)
        # Of 2026 only the part after the balance sheet counts: the rest is already in the 10-Q bridge
        H = 10 # total years
        ev0 = self.first_year_fraction * fcff_vector[0] * df_vector[0]
        for i in range(1, H):
            ev0 += fcff_vector[i] * df_vector[i]
        ev0 += TV * df_vector[H-1]
        return ev0
    
    

if __name__ =="__main__":
    ## 1. SETUP AND CALCULATE WACC
    # Values Test: D13 v2 (expected WACC 0.0675 growth, 0.0688 maturity)
    price_share = 128.34   # close 2026-10-08, the valuation date
    beta = 0.5110          # peers of D09 with Blume, from beta_calculator.py
    beta_maturity = 0.55   # G3 assumption: average 60-month beta, 2016-2026 (calcoli/beta_storico.ps1)
    tax = 0.21             # WACC: marginal rate (H10)
    tax_nopat_inf = 0.21   # G2: NOPAT rate goes from 19% to 21% in years 6-10 (guide), so 21% in year 11 (H10)
    first_year_fraction = 112 / 364  # 2026-09-06 to 2026-12-26, out of the 364 days of fiscal 2026
    first_discount_period = 79 / 364 # 2026-10-08 to 2026-12-26
    g_inf = 0.025          # From G1 (D05)

    calc = WaccCalculator(price_share, beta, tax)
    w_growth = calc.calculate_wacc_base()
    w_maturity = WaccCalculator(price_share, beta_maturity, tax).calculate_wacc_base()
    vector = calc.generate_wacc_vector(w_growth,w_maturity)
    print(f"----- Executing WACC -----")
    print(f'Vector WACC (10 years):', [round(w,4) for w in vector])
    print(f'WACC growth: {w_growth:.4f}, WACC maturity: {w_maturity:.4f}\n')


    ## 2. SETUP AND CALCULATE Terminal Value and Enterprise Value
    # Temporary values only for R_h and FCFF vector ()
    r_h_stochastic = 110.0  # USD bn
    fcff_test_vector = [11.0, 11.5, 12.0, 12.2, 12.5, 12.8, 13.0, 13.2, 13.5, 13.8]
    
    val_calc = ValueCalculator(g_inf, tax_nopat_inf, first_year_fraction, first_discount_period)
    df_factors = val_calc.calculate_discount_factors(vector)

    scenari = {                        # D21 dati:
        "Bear": {
            "m_inf": 0.135,            # Margine 13.5%
            "s_inf": 0.000             # Spread nullo
        },
        "Base": {  
            "m_inf": 0.145,            # Margine 14.5%
            "s_inf": 0.015             # Spread piccolo (limite superiore per Wide Moat)
        },
        "Growth": {         
            "m_inf": 0.155,            # Margine 15.5%
            "s_inf": 0.025             # Spread moderato (limite inferiore per Mean Reversion)
        }
    }
    print(f"\n----- Executing Terminal Value and Enterprise Value -----")
    for scenario, values in scenari.items():
        # Adjusting the ROIC_inf for each scenario based on the s_inf value
        nopat_h1 = val_calc.calculate_nopat_h1(r_h = r_h_stochastic, m_inf = values["m_inf"])
        roic_inf = w_maturity + values["s_inf"]
        
        tv = val_calc.calculate_terminal_value(nopat_h1, w_maturity, roic_inf)
        ev = val_calc.calculate_enterprise_value(tv, df_factors, fcff_test_vector)

        print(f"Scenario: {scenario}")
        print(f"Spread applicato (s_inf): {values['s_inf']*100:.2f}%")
        print(f"Terminal Value (TV): {tv:.3f} USD bn")
        print(f"Enterprise Value (EV): {ev:.3f} USD bn\n")