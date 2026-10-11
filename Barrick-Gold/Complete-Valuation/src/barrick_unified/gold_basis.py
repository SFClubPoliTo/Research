"""Origin-only deterministic GLD/physical-gold basis transformation."""
import numpy as np
import pandas as pd


def forecast_log_basis(observations, origin, target, *, minimum_prices=253):
    """Fit log(GLD USD/share / gold USD/oz) using dates <= origin.

    Target prices are neither required nor accessed. The fitted trend is an
    empirical conditional basis, not an identified long-run conversion law.
    """
    origin=pd.Timestamp(origin);target=pd.Timestamp(target)
    if target<=origin:
        raise ValueError('target must follow origin')
    data=observations[['date','gld_usd_share','gold_midpoint_usd_oz']].copy()
    data['date']=pd.to_datetime(data.date)
    data=data[data.date<=origin].sort_values('date')
    if data.date.duplicated().any() or len(data)<minimum_prices or data.date.iloc[-1]!=origin:
        raise ValueError('unique sufficient history including exact origin required')
    prices=data[['gld_usd_share','gold_midpoint_usd_oz']].to_numpy(float)
    if not np.isfinite(prices).all() or (prices<=0).any():
        raise ValueError('finite positive synchronized prices required')
    times=(data.date-data.date.iloc[0]).dt.total_seconds().to_numpy()/(365.25*86400)
    slope,intercept=np.polyfit(times,np.log(prices[:,0]/prices[:,1]),1)
    horizon=(target-data.date.iloc[0]).total_seconds()/(365.25*86400)
    return dict(log_ratio_prediction=float(intercept+slope*horizon),
                annual_log_ratio_trend=float(slope),training_prices=len(data),
                training_first=str(data.date.iloc[0].date()),training_last=str(origin.date()),
                gold_origin=float(prices[-1,1]),gld_origin=float(prices[-1,0]))


def gld_forecast_to_gold(mean, quantiles, basis_prediction):
    """Convert conditional means/quantiles with a deterministic fitted ratio.

    Stochastic basis and parameter uncertainty are omitted, not implicitly
    integrated by division. Input/output units are USD/share and USD/oz.
    """
    values=np.asarray(quantiles,float)
    if values.shape!=(5,) or not np.isfinite(values).all() or (values<=0).any() or (np.diff(values)<0).any():
        raise ValueError('five positive ordered finite GLD quantiles required')
    if not np.isfinite(mean) or mean<=0 or not np.isfinite(basis_prediction):
        raise ValueError('positive GLD mean and finite log basis required')
    scale=np.exp(-basis_prediction)
    return float(mean*scale),(values*scale).tolist()
