"""Exact irregular-time GBM likelihood, with explicit physical drift.

Historical-only estimates are benchmarks. Fixing sigma to a same-date Q
estimate is a restricted P/Q bridge for the SAME traded underlying, never an
ETF-to-gold conversion. Neither identifies future regime stability.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class GBMFit:
    arithmetic_drift: float
    log_drift: float
    sigma: float
    drift_standard_error: float
    years: float
    observations: int
    diffusion_source: str


def fit_gbm(log_returns,year_fractions,*,sigma_q=None):
    r=np.asarray(log_returns,dtype=float);dt=np.asarray(year_fractions,dtype=float)
    if r.ndim!=1 or r.shape!=dt.shape or len(r)<2 or not np.isfinite(r).all() or not np.isfinite(dt).all() or (dt<=0).any():
        raise ValueError('finite aligned returns and positive time gaps required')
    a=float(r.sum()/dt.sum())
    if sigma_q is None:
        sigma=float(np.sqrt(np.mean((r-a*dt)**2/dt)))
        source='historical_P_MLE_not_joint_Q_fit'
    else:
        if not np.isfinite(sigma_q) or sigma_q<=0:raise ValueError('positive Q diffusion required')
        sigma=float(sigma_q);source='same_underlying_Q_diffusion_held_fixed'
    return GBMFit(a+.5*sigma*sigma,a,sigma,sigma/np.sqrt(dt.sum()),float(dt.sum()),len(r),source)


def predictive_log_score(log_return,dt,fit):
    if not np.isfinite(dt) or dt<=0 or fit.sigma<=0:raise ValueError('invalid predictive variance')
    variance=fit.sigma**2*dt
    return -.5*(np.log(2*np.pi*variance)+(log_return-fit.log_drift*dt)**2/variance)
