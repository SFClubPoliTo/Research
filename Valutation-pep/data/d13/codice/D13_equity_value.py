
'''
Module: Equity Bridge (G3)
    
    - Calculates the Enterprise-to-Equity value bridge for PepsiCo (PEP).
    - Bridges Operating Enterprise Value (EV) to Total Equity Value and
      computes the final value per share based on diluted shares.
'''

class EquityBridge:
    def __init__(self, bridge_inputs, diluted_shares, provisional=()):
        # Initializing bridge with a dictionary of values in USD billions
        self.bridge_inputs = bridge_inputs
        self.diluted_shares = diluted_shares
        self.provisional = list(provisional) # names of items still provisional

        self.bridge_total = sum(self.bridge_inputs.values())

    def assert_final(self):
        # Final run: no provisional item allowed
        if self.provisional:
            raise ValueError(f"Provisional bridge items: {', '.join(self.provisional)}")

    def calculate_value_share(self, ev_oper):
        equity_value = ev_oper + self.bridge_total
        price_per_share = equity_value / self.diluted_shares

        breakdown = {"Operating Enterprise Value": ev_oper}
        breakdown.update(self.bridge_inputs)
        breakdown.update({
            "Equity value": equity_value,
            "Diluted shares (bn)": self.diluted_shares,
            "Value per share (USD)": price_per_share
        })
        return equity_value, price_per_share, breakdown

if __name__=="__main__":
    # Valuation date 2026-10-08 (H01): balance sheet of the 10-Q at 2026-09-05; flows from 2026-09-06 (D13_wacc_terminal.py)
    # D03 (accepted by G2): operating leases (3.846) and JVs (2.215) stay in the flows, not here
    # Euro notes (settled 2026-10-16, 424B2) come after the valuation date: not in the bridge
    # TCJA transition tax (0.965) already paid by 2026-09-05 (10-Q p. 48): cash is net of it, not in the bridge (agreed with G2)
    tax = 0.21 # H10: same rate as the WACC
    data_bridge = {
        "Cash and cash equivalents": 10.675,         # 10-Q p. 6, 2026-09-05
        "Short-term investments": 0.488,             # 10-Q p. 6
        "Tropicana Brands Group (39%)": 0.0,         # 10-K p. 96, fully written down
        "Celsius convertible preferred (fair value)": 1.482, # 10-Q p. 22
        "Short-term debt obligations": -9.223,       # 10-Q p. 6
        "Long-term debt obligations": -42.658,       # 10-Q p. 6
        "Cash restricted in Russia (20%)": 0.0,      # 10-Q p. 48: amounts under currency controls not material; counted in full, like the Russian flows
        "Pension and retiree medical deficits, after tax": -(0.233 + 0.468) * (1 - tax), # 10-K p. 86; foreign surplus excluded
        "Non-controlling interests": -0.195,         # 10-Q p. 6; H13: book value (about 0.14 USD per share)
        "Receivables from TBG (Juice Transaction)": 0.0, # 10-K p. 106, noncurrent, amount not disclosed; out of NWC (G2)
        "Dividends payable": -(1.967 + 6.004 - 5.935) # estimate: 10-K p. 106 + declared 10-Q p. 7 - paid 10-Q p. 5; ex-dividend 2026-09-04, not received by those who buy on 2026-10-08; out of NWC (G2)
    }
    diluted_shares = 1.366 # 10-Q cover and p. 26; H12: treasury stock method, as PepsiCo
    provisional = [] # H12, H13 and Russian cash decided (G3, 2026-11-12)
    bridge = EquityBridge(data_bridge, diluted_shares, provisional)
    bridge.assert_final() # stops the run if an item is still provisional
    print(f'total sum of the bridge: {bridge.bridge_total:.3f} USD bn') # expected -42.021

    # Test
    ev_test = 250.0
    eq_val, p_share, details = bridge.calculate_value_share(ev_test)

    print(f'\n Results with EV_oper = {ev_test} USD bn: \n')
    print(f'Equity Value: {eq_val:.3f} USD bn\n')
    print(f'Price per share (P): {p_share:.2f} USD')