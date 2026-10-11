"""Experimental likelihood for a restricted, same-underlying P/Q model.

Bootstrap particle filter for the Euler observation/state system. The Q
coefficients are fixed inputs; price and variance Brownian premia and marked
point-process tilts are estimated separately. This module alone does not
certify continuous-time convergence or a physical commodity/DCF forecast.
"""
import numpy as np
from scipy.special import logsumexp
from scipy.stats import poisson


def physical_filter(returns,dt,carry,q,premia,*,particles=512,seed=704,return_diagnostics=False,substeps=1,
                    integrate_marks=False, integrate_poisson_counts=False):
    """premia=(eta_price, log(kappa_P/kappa_Q), log(c), mark_shift_in_SD).

    State lambda is the Q-intensity functional of the same event history;
    event arrivals under P have intensity c*lambda. Normal marks are tilted
    by b=mark_shift_in_SD/sigma_J. rho and xi are shared across measures.
    Filtering starts from theta_P and the stationary mean intensity functional;
    both are initialization assumptions, assessed by training burn-in.

    With integrate_marks=True, normal marks are integrated analytically in
    the observation density conditional on counts. This is valid because
    marks do not enter the variance or the nonmark-dependent Hawkes state.
    Counts and variance remain particle sampled. Default preserves old runs.
    For constant Poisson intensity only, integrate_poisson_counts also sums
    the daily count mixture (omitted count probability at most 1e-12).
    This is not valid for self-exciting Hawkes intensity and is rejected there.
    """
    r=np.asarray(returns,float);dt=np.asarray(dt,float);carry=np.asarray(carry,float)
    if r.ndim!=1 or r.shape!=dt.shape or r.shape!=carry.shape or len(r)==0:
        raise ValueError('aligned nonempty return/time/carry arrays required')
    if not np.isfinite(np.concatenate([r,dt,carry])).all() or (dt<=0).any():raise ValueError('invalid observations')
    if particles<16:raise ValueError('at least 16 particles required')
    if not isinstance(substeps,int) or substeps<1:raise ValueError('positive integer substeps required')
    eta,log_k,log_c,mark_shift=map(float,premia)
    if not np.isfinite([eta,log_k,log_c,mark_shift]).all():raise ValueError('nonfinite premia')
    kq,tq,xi,rho=(q[x] for x in ['kappa','theta','xi','rho'])
    if min(kq,tq,xi)<=0 or abs(rho)>=1:raise ValueError('invalid Q diffusion')
    kp=kq*np.exp(log_k);tp=kq*tq/kp;c=np.exp(log_c)
    alpha=q.get('alpha',0.);beta=q.get('beta',1.);baseline=q.get('lambda_bar',q.get('lambd',0.))
    if integrate_poisson_counts and alpha != 0:
        raise ValueError('count integration requires constant Poisson intensity')
    if integrate_poisson_counts:
        integrate_marks=True
    if min(alpha,baseline)<0 or beta<=0 or c*alpha>=beta:raise ValueError('nonstationary physical intensity')
    muq=q.get('mu_J',0.);sj=q.get('sigma_J',0.);mup=muq+mark_shift*sj
    kJ=np.expm1(muq+.5*sj*sj)
    v=np.full(particles,tp);lam=np.full(particles,baseline/(1-c*alpha/beta))
    rng=np.random.default_rng(seed);nll=0.;floor_count=0;min_ess=particles;log_scores=[]
    log2pi=np.log(2*np.pi)
    for y,h,rate in zip(r,dt,carry):
        # Integrate the unobserved intraday state, then weight the aggregate
        # daily return. Independent price Brownian increments integrate out
        # conditionally; do not resample against fabricated intraday prices.
        mean=np.zeros(particles);obsvar=np.zeros(particles);step=h/substeps
        for _ in range(substeps):
            z=rng.standard_normal(particles)
            count=rng.poisson(c*lam*step) if baseline or alpha else np.zeros(particles)
            mark_noise=rng.standard_normal(particles) # Preserve CRN stream alignment.
            jumps=0. if integrate_poisson_counts else (count*mup if integrate_marks else count*mup+np.sqrt(count)*sj*mark_noise)
            positive=np.maximum(v,1e-10);root=np.sqrt(positive*step)
            mean+=(rate+(eta-.5)*positive-lam*kJ)*step+rho*root*z+jumps
            obsvar+=(1-rho*rho)*positive*step
            if integrate_marks and not integrate_poisson_counts:
                obsvar+=count*sj*sj
            newv=v+kp*(tp-positive)*step+xi*root*z
            floor_count+=int(np.sum(newv<0));v=np.maximum(newv,1e-10)
            lam=np.maximum(lam+beta*(baseline-lam)*step+alpha*count,0.)
        logw=-.5*(log2pi+np.log(obsvar)+(y-mean)**2/obsvar)
        if integrate_poisson_counts and baseline:
            rate_count=c*baseline*h
            max_count=int(poisson.ppf(1-1e-12,rate_count))
            if max_count>10000:
                raise ValueError('Poisson mixture exceeds supported count budget')
            logw=np.full(particles,-np.inf)
            for number in range(max_count+1):
                variance=obsvar+number*sj*sj
                component=(poisson.logpmf(number,rate_count)
                    -.5*(log2pi+np.log(variance)+(y-mean-number*mup)**2/variance))
                logw=np.logaddexp(logw,component)
        score=logsumexp(logw)-np.log(particles)
        if not np.isfinite(score):raise ValueError('nonfinite likelihood')
        nll-=score;log_scores.append(float(score))
        weights=np.exp(logw-logsumexp(logw));min_ess=min(min_ess,1/np.sum(weights**2))
        points=(rng.random()+np.arange(particles))/particles
        cdf=np.cumsum(weights);cdf[-1]=1.
        indices=np.searchsorted(cdf,points)
        v=v[indices];lam=lam[indices]
    if return_diagnostics:
        return dict(negative_log_likelihood=float(nll),terminal_variance_mean=float(v.mean()),
                    terminal_q_intensity_functional_mean=float(lam.mean()),kappa_p=float(kp),theta_p=float(tp),
                    intensity_ratio=float(c),mark_mean_p=float(mup),
                    substeps=substeps,variance_floor_fraction=floor_count/(len(r)*particles*substeps),minimum_ess=float(min_ess),
                    normal_marks_integrated=bool(integrate_marks),
                    poisson_counts_integrated=bool(integrate_poisson_counts),
                    log_scores=log_scores)
    return float(nll)
