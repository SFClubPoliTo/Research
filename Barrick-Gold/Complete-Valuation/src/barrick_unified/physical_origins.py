"""Recover dated observed option inputs without importing forecast outputs."""
import numpy as np
import pandas as pd

OBSERVED_COLUMNS = ('date', 'expiry', 'K', 'T', 'dte', 'spot', 'price', 'rate',
                    'curve_date', 'implied_vol', 'vega', 'conId', 'localSymbol')


def observed_origin_surface(frame, origin, *, budget=64, minimum=64):
    """Use only that day's market fields in the frozen per-contract OOS table.

    A day formerly used as a target can later be a forecast origin. Its own
    observed prices are then training information; earlier model forecasts,
    benchmark IVs and support flags must never enter this reconstruction.
    Selection is deterministic maximin in current log-moneyness/sqrt-maturity.
    """
    if not isinstance(budget, int) or not isinstance(minimum, int) or not 1<=minimum<=budget:
        raise ValueError('positive integer minimum <= budget required')
    missing=set(OBSERVED_COLUMNS)-set(frame.columns)
    if missing:
        raise ValueError(f'missing observed market columns: {sorted(missing)}')
    day=pd.Timestamp(origin).normalize()
    dates=pd.to_datetime(frame['date']).dt.normalize()
    available=frame.loc[dates.eq(day)].copy()
    if available.empty:
        raise ValueError('no observed option surface at requested origin')
    if 'target_date' in available:
        if not pd.to_datetime(available.target_date).dt.normalize().eq(day).all():
            raise ValueError('inconsistent observation date')
    curves=pd.to_datetime(available.curve_date,errors='coerce').dt.normalize()
    if curves.isna().any() or curves.gt(day).any():
        raise ValueError('curve unavailable or later than forecast origin')
    if 'timestamp' in available:
        timestamps=pd.to_datetime(available.timestamp,utc=True,errors='coerce')
        if timestamps.isna().any() or timestamps.dt.tz_localize(None).dt.normalize().gt(day).any():
            raise ValueError('timestamp unavailable or later than forecast origin')
    available=available.loc[:, list(OBSERVED_COLUMNS)]
    numeric=available[['K','T','dte','spot','price','rate','implied_vol','vega']].to_numpy(float)
    if not np.isfinite(numeric).all():
        raise ValueError('nonfinite observed market input')
    if (available[['K','T','spot','implied_vol']]<=0).any().any():
        raise ValueError('positive strike, maturity, spot and IV required')
    if available.spot.nunique()!=1:
        raise ValueError('one underlying spot is required at each origin')
    available=available.loc[(available.dte>=75)&(available.price>=0)&(available.vega>=0)]
    available=available.sort_values(['expiry','K','conId']).drop_duplicates(['expiry','K']).reset_index(drop=True)
    if len(available)<minimum or available.expiry.nunique()<3:
        raise ValueError('insufficient dated quotes or expiries for dense-origin calibration')
    if len(available)<=budget:
        return available
    xy=np.column_stack([np.log(available.K.to_numpy()/available.spot.to_numpy()),
                        np.sqrt(available['T'].to_numpy())])
    scale=np.ptp(xy,axis=0);scale[scale==0]=1.
    xy=(xy-xy.min(axis=0))/scale
    chosen=[0];distance=np.sum((xy-xy[0])**2,axis=1)
    for _ in range(1,budget):
        distance[chosen]=-1.
        index=int(np.argmax(distance));chosen.append(index)
        distance=np.minimum(distance,np.sum((xy-xy[index])**2,axis=1))
    return available.iloc[sorted(chosen)].reset_index(drop=True)
