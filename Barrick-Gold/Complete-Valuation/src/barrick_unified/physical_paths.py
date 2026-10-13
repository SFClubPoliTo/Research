"""Conditional physical paths on the same underlying and initial state as Q.

The exact family has a restricted finite-horizon density construction. These
paths use a full-truncation Euler/Poisson time grid and require their own
numerical refinement. Premium inputs must retain estimation provenance.
"""
from dataclasses import dataclass
import math
import numpy as np
from .physical_measure import restricted_joint_entropy_bound


@dataclass(frozen=True)
class PhysicalPaths:
    model: str
    price_endpoints: np.ndarray
    price_interval_means: np.ndarray
    times: np.ndarray
    diagnostics: dict
    measure: str = 'P'


def simulate_physical_paths(model, q, premia, *, initial_price, output_times,
                            underlying_kind, contract_expiry_time=None,
                            n_paths=8192, steps_per_year=252, carry_q=.04,
                            physical_gbm_drift=None, seed=104):
    """premia=(eta_S, log(kappa_P/kappa_Q), log(c), mark shift in SD).

    P starts from the dated Q-calibration state v0/lambda0, rather than
    substituting the unconditional physical mean. Price carry is r-q for the
    same spot/ETF, or zero for a fixed-delivery futures model. No WACC enters.
    Interval means are time-weighted trapezoidal averages of simulated prices,
    not realized selling-price forecasts or a corporate cash-flow model.
    """
    if model not in ['black_scholes','heston','bates','full_bates_hawkes']:
        raise ValueError('unknown physical model family')
    times=np.asarray(output_times,float)
    if times.ndim!=1 or not len(times) or not np.isfinite(times).all() or times[0]<=0 or (np.diff(times)<=0).any():
        raise ValueError('strictly increasing positive finite output times required')
    if not isinstance(n_paths,int) or n_paths<1 or not isinstance(steps_per_year,int) or steps_per_year<1:
        raise ValueError('positive integer path and time resolution required')
    if not math.isfinite(initial_price) or initial_price<=0 or not math.isfinite(carry_q):
        raise ValueError('positive price and finite pricing carry required')
    if underlying_kind not in ['spot_or_etf','fixed_delivery_future']:
        raise ValueError('declare the underlying as spot/ETF or a fixed-delivery future')
    if underlying_kind=='fixed_delivery_future':
        if contract_expiry_time is None or not math.isfinite(contract_expiry_time) or contract_expiry_time<=0:
            raise ValueError('fixed-delivery futures require their remaining contract lifetime')
        if times[-1]>contract_expiry_time:
            raise ValueError('a fixed-delivery futures path cannot continue beyond contract expiry')
        if abs(carry_q)>1e-12:
            raise ValueError('fixed-delivery futures require zero Q price drift with deterministic rates')
    shifts=np.asarray(premia,float)
    if shifts.shape!=(4,) or not np.isfinite(shifts).all():
        raise ValueError('four finite physical premia required')
    eta,log_k,log_c,mark_shift=map(float,shifts)
    streams=[np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(3)]
    gbm=model=='black_scholes'
    if gbm:
        sigma=float(q['sigma'])
        if not math.isfinite(sigma) or sigma<=0 or physical_gbm_drift is None or not math.isfinite(physical_gbm_drift):
            raise ValueError('GBM requires its same-underlying Q diffusion and an explicit finite physical drift')
        v0=sigma*sigma;rho=0.;xi=0.;kp=0.;tp=v0
        lam0=baseline=alpha=beta=muq=std=kJ=0.;c=1.;mup=0.
        certificate={'status':'CONSTANT_DIFFUSION_GBM_FINITE_HORIZON',
                     'empirical_or_discrete_likelihood_admission':False}
    else:
        v0=float(q['v0']);kq=float(q['kappa']);tq=float(q['theta'])
        xi=float(q.get('xi',q.get('sigma')));rho=float(q['rho'])
        if not all(math.isfinite(x) for x in [v0,kq,tq,xi,rho]) or min(kq,tq,xi)<=0:
            raise ValueError('finite positive CIR coefficients required')
        kp=kq*math.exp(log_k);tp=kq*tq/kp;c=math.exp(log_c)
        jump_model=model in ['bates','full_bates_hawkes']
        baseline=float(q.get('lambda_bar',q.get('lambd',0.))) if jump_model else 0.
        lam0=float(q.get('lambda0',baseline)) if jump_model else 0.
        alpha=float(q.get('alpha',0.)) if model=='full_bates_hawkes' else 0.
        beta=float(q.get('beta',0.)) if model=='full_bates_hawkes' else 0.
        muq=float(q.get('mu_J',0.)) if jump_model else 0.
        std=float(q.get('sigma_J',0.)) if jump_model else 0.
        if not math.isfinite(muq):raise ValueError('nonfinite normal mark mean')
        if alpha and (beta<=0 or alpha>=beta or c*alpha>=beta):
            raise ValueError('both Hawkes laws must satisfy the stated stationarity restriction')
        certificate=restricted_joint_entropy_bound(
            horizon=float(times[-1]),variance0=v0,kappa_q=kq,theta_q=tq,xi=xi,
            rho=rho,eta_price=eta,eta_variance=(kq-kp)/xi,
            lambda0=lam0,baseline=baseline,alpha=alpha,beta=beta,
            intensity_ratio=c,mark_tilt=mark_shift/std if std else 0.,mark_std=std)
        mup=muq+mark_shift*std;kJ=math.expm1(muq+.5*std*std)
    price=np.full(n_paths,initial_price,float);v=np.full(n_paths,v0);lam=np.full(n_paths,lam0)
    endpoints=np.empty((n_paths,len(times)));averages=np.empty_like(endpoints)
    previous=0.;floor_count=total_steps=0
    for column,end in enumerate(times):
        interval=end-previous;steps=max(1,math.ceil(interval*steps_per_year));h=interval/steps
        accumulated=np.zeros(n_paths)
        for _ in range(steps):
            old=price.copy();positive=np.maximum(v,1e-10)
            z_s,z_v_independent=streams[0].standard_normal((2,n_paths))
            z_v=rho*z_s+np.sqrt(1-rho*rho)*z_v_independent
            counts=streams[1].poisson(c*lam*h)
            jumps=counts*mup+np.sqrt(counts)*std*streams[2].standard_normal(n_paths)
            drift=physical_gbm_drift-.5*positive if gbm else carry_q+(eta-.5)*positive-lam*kJ
            price=old*np.exp(drift*h+np.sqrt(positive*h)*z_s+jumps)
            accumulated+=(old+price)*(.5*h)
            if not gbm:
                new_v=v+kp*(tp-positive)*h+xi*np.sqrt(positive*h)*z_v
                floor_count+=int(np.sum(new_v<0));v=np.maximum(new_v,1e-10)
                lam=baseline+(lam-baseline)*np.exp(-beta*h)+alpha*counts
            total_steps+=1
        if not np.isfinite(price).all():raise ValueError('nonfinite physical price path')
        endpoints[:,column]=price;averages[:,column]=accumulated/interval
        previous=end
    diagnostics=dict(seed=seed,n_paths=n_paths,steps_per_year=steps_per_year,total_steps=total_steps,
                     underlying_kind=underlying_kind,contract_expiry_time=contract_expiry_time,
                     variance_floor_fraction=floor_count/(n_paths*total_steps),
                     shared_origin_variance=v0,shared_origin_q_intensity_functional=lam0,
                     density_bound=certificate,
                     discretization='full-truncation Euler variance; frozen-intensity Poisson jumps; right-endpoint excitation',
                     corporate_or_predictive_admission=False)
    return PhysicalPaths(model,endpoints,averages,times,diagnostics)
