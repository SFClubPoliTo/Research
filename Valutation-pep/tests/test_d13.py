import importlib.util
from pathlib import Path
import numpy as np
import yaml
from src.rates.model import compute_enterprise_value
from src.bridge.model import compute_equity_and_price

ROOT = Path(__file__).resolve().parents[1]
def test_d13_matches_delivery():
    cfg=yaml.safe_load((ROOT/'config/config.yaml').read_text())
    path=ROOT/'data/d13/codice/D13_wacc_terminal.py'
    spec=importlib.util.spec_from_file_location('g3',path)
    g3=importlib.util.module_from_spec(spec); spec.loader.exec_module(g3)
    r=cfg['rates_and_terminal']
    growth=g3.WaccCalculator(128.34,.511,.21)
    maturity=g3.WaccCalculator(128.34,.55,.21).calculate_wacc_base()
    w=growth.generate_wacc_vector(growth.calculate_wacc_base(),maturity)
    delivery=yaml.safe_load((ROOT/'data/d13/consegne/D13_config_v2_G3.yaml').read_text())['rates']
    w = delivery['wacc_by_year']
    maturity = delivery['wacc_maturity']
    val=g3.ValueCalculator(.025,.21,112/364,79/364)
    df=val.calculate_discount_factors(w)
    revenues=np.array([np.linspace(94,110,10),np.linspace(94,140,10)])
    flows=np.array([np.linspace(10,14,10),np.linspace(11,18,10)])
    original=flows.copy()
    out=compute_enterprise_value(revenues,flows,r)
    tv=val.calculate_terminal_value(val.calculate_nopat_h1(revenues[:,-1],r['margin_terminal']),maturity,.20)
    expected=[val.calculate_enterprise_value(tv[i],df,flows[i]) for i in range(2)]
    np.testing.assert_allclose(out['ev'],expected,rtol=1e-13)
    np.testing.assert_array_equal(flows,original)
    np.testing.assert_allclose(out['df_vector'],df)
    bridge=compute_equity_and_price(out['ev'],cfg['bridge'],is_final_run=True)
    assert abs(bridge['bridge_total']-(-42.02079))<1e-10
    np.testing.assert_allclose(bridge['share_price'],(out['ev']-42.02079)/1.366)
