"""Origin-selected, same-delivery futures returns for physical diagnostics."""
import numpy as np
import pandas as pd


def origin_selected_returns(panel, *, minimum_volume=100, minimum_days_to_expiry=30):
    """Choose delivery using only origin quotes, then score that delivery.

    The nearest eligible delivery is selected at the origin. A missing or
    illiquid target is recorded as an exclusion, never used to select another
    contract retrospectively. Calendar is the union of observed dates; no
    filling. These are rotating-delivery log price changes, not a spot level
    series or collateralized portfolio total returns.
    """
    data=panel.copy()
    required={'date','contract','expiry','close','volume'}
    if not required.issubset(data.columns):raise ValueError('missing panel columns')
    data['date']=pd.to_datetime(data.date);data['expiry']=pd.to_datetime(data.expiry)
    if data.duplicated(['date','contract']).any():raise ValueError('duplicate contract/date')
    if minimum_volume<0 or minimum_days_to_expiry<0:raise ValueError('negative selection threshold')
    dates=sorted(data.date.unique());rows=[]
    for origin,target in zip(dates[:-1],dates[1:]):
        eligible=data[(data.date==origin)&(data.volume>=minimum_volume)&(data.close>0)&
                      (data.expiry>=origin+pd.Timedelta(days=minimum_days_to_expiry))].sort_values(['expiry','contract'])
        row=dict(origin=origin,target=target,status='NO_ELIGIBLE_ORIGIN')
        if not eligible.empty:
            selected=eligible.iloc[0]
            row.update(contract=selected.contract,expiry=selected.expiry,origin_close=float(selected.close),origin_volume=float(selected.volume))
            future=data[(data.date==target)&(data.contract==selected.contract)]
            row['status']='MISSING_TARGET'
            if not future.empty:
                observed=future.iloc[0]
                row.update(target_close=float(observed.close),target_volume=float(observed.volume))
                row['status']='ILLIQUID_TARGET'
                if observed.volume>=minimum_volume and observed.close>0:
                    row.update(status='ACCEPTED',log_return=float(np.log(observed.close/selected.close)),
                               dt_years=float((target-origin)/pd.Timedelta(days=365.25)))
        rows.append(row)
    return pd.DataFrame(rows)
