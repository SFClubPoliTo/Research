"""Batched execution of the existing HFT1 Bernoulli-fill accounting model.

Only the path loop is vectorized. Quotes are fixed for both sides within a
step, bid accounting is applied before ask accounting, and random draw order
matches the original Monte Carlo generator.
"""
import numpy as np


def scalar_paths(prices, ub, ua, sigma, gamma, decay, arrival, horizon, dt, inventory_aware, gbm=False):
    count, steps = ub.shape
    q = np.zeros(count, dtype=np.int64)
    cash = np.zeros(count)
    delta = np.log1p(gamma / decay) / gamma
    for step in range(steps):
        s = prices[:, step]
        tau = max(horizon - step * dt, 1e-9)
        variance = (sigma * s)**2 if gbm else sigma**2
        center = s - q * gamma * variance * tau if inventory_aware else s
        bid, ask = center - delta, center + delta
        p_bid = 1.0 - np.exp(-arrival * np.exp(-decay * np.maximum(s-bid, 0.0)) * dt)
        p_ask = 1.0 - np.exp(-arrival * np.exp(-decay * np.maximum(ask-s, 0.0)) * dt)
        buy = ub[:, step] < p_bid
        sell = ua[:, step] < p_ask
        q += buy
        cash -= np.where(buy, bid, 0.)
        q -= sell
        cash += np.where(sell, ask, 0.)
    return cash + q * prices[:, -1], q


def multivariate_paths(prices, ub, ua, sigma, gamma, decay, arrival, horizon, dt, inventory_aware):
    count, steps, dimension = ub.shape
    q = np.zeros((count, dimension), dtype=np.int64)
    cash = np.zeros(count)
    liquidity = np.log1p(gamma / decay) / gamma
    for step in range(steps):
        s = prices[:, step]
        tau = max(horizon - step*dt, 0.)
        center = s-gamma*tau*(q@sigma.T) if inventory_aware else s
        risk_half = .5*gamma*tau*np.diag(sigma) if inventory_aware else 0.
        bid, ask = center-risk_half-liquidity, center+risk_half+liquidity
        p_bid = 1.0-np.exp(-arrival*np.exp(-decay*np.maximum(s-bid,0.))*dt)
        p_ask = 1.0-np.exp(-arrival*np.exp(-decay*np.maximum(ask-s,0.))*dt)
        buy = ub[:, step] < p_bid
        sell = ua[:, step] < p_ask
        q += buy
        cash -= np.sum(bid*buy,axis=1)
        q -= sell
        cash += np.sum(ask*sell,axis=1)
    return cash+np.sum(q*prices[:,-1],axis=1), q


def scalar_mc(parameters, *, gbm=False, seed=1000):
    p=parameters; n=p['n_steps']; count=p['N_MC']
    rng=np.random.default_rng(seed)
    dw=rng.normal(0,np.sqrt(p['dt']),(count,n))
    ub=rng.random((count,n));ua=rng.random((count,n))
    price=np.empty((count,n+1));price[:,0]=p['S0']
    sigma=p['sigma_GBM'] if gbm else p['sigma_BM']
    for step in range(n):
        price[:,step+1]=price[:,step]*np.exp((p['mu_GBM']-.5*sigma*sigma)*p['dt']+sigma*dw[:,step]) if gbm else price[:,step]+sigma*dw[:,step]
    args=(price,ub,ua,sigma,p['gamma'],p['k'],p['A'],p['T'],p['dt'])
    pn,qn=scalar_paths(*args,False,gbm=gbm)
    pa,qa=scalar_paths(*args,True,gbm=gbm)
    return {'pnl_n':pn,'pnl_as':pa,'inv_n':qn,'inv_as':qa}


def multi_mc(parameters,multi,sigma,chol,seed=3000):
    n=parameters['n_steps'];count=multi['N_MC'];dim=len(multi['S0']);dt=parameters['dt']
    rng=np.random.default_rng(seed)
    dw=rng.normal(0,np.sqrt(dt),(count,n,dim))
    ub=rng.random((count,n,dim));ua=rng.random((count,n,dim))
    price=np.empty((count,n+1,dim));price[:,0]=multi['S0']
    increments=dw@chol.T
    price[:,1:]=multi['S0']+np.cumsum(increments,axis=1)
    args=(price,ub,ua,sigma,parameters['gamma'],multi['k'],multi['A'],parameters['T'],dt)
    pn,qn=multivariate_paths(*args,False);pa,qa=multivariate_paths(*args,True)
    return {'pnl_n':pn,'pnl_as':pa,'gross_n':np.sum(abs(qn),axis=1),'gross_as':np.sum(abs(qa),axis=1),
            'risk_n':np.sqrt(np.einsum('ni,ij,nj->n',qn,sigma,qn)), 'risk_as':np.sqrt(np.einsum('ni,ij,nj->n',qa,sigma,qa))}
