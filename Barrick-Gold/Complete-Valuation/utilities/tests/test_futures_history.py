import numpy as np
import pandas as pd
from barrick_unified.futures_history import origin_selected_returns


def fixture():
    rows=[]
    for date,a,b in [('2026-01-01',100,150),('2026-01-02',101,153),('2026-01-05',102,156)]:
        for name,expiry,price in [('near','2026-01-31',a),('far','2026-03-31',b)]:
            rows.append(dict(date=date,contract=name,expiry=expiry,close=price,volume=200))
    return pd.DataFrame(rows)


def test_roll_uses_two_prices_of_same_contract():
    result=origin_selected_returns(fixture())
    assert list(result.contract)==['near','far']
    assert np.allclose(result.log_return,[np.log(101/100),np.log(156/153)])


def test_target_information_cannot_change_origin_selection():
    panel=fixture();panel.loc[(panel.date=='2026-01-02')&(panel.contract=='near'),'volume']=0
    result=origin_selected_returns(panel)
    assert result.iloc[0].contract=='near'
    assert result.iloc[0].status=='ILLIQUID_TARGET'
    assert pd.isna(result.iloc[0].get('log_return'))
