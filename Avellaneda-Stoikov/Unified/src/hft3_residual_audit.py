"""Off-grid full-HJB diagnostic including covariance derivatives, not a P3 fit."""
import json
import numpy as np
from scipy.interpolate import RectBivariateSpline
from layout import OUTPUTS, output_dir
from hft3_policy import Policy
from hft3_multiasset_model import psd_factor


def hamiltonian(gain):
    delta = np.clip(np.log1p(.2/1.15)/.2-gain, .02, 4)
    return 14*np.exp(-1.15*delta)*(-np.expm1(-.2*(delta+gain)))/.2


def main():
    p = Policy()
    splines = [RectBivariateSpline(p.times, p.y, p.value[:, i], kx=3, ky=3, s=0) for i in range(13)]
    rng = np.random.default_rng(20261013)
    samples = 1500
    rates = np.tile(np.geomspace(3, 180, 6), 2)
    weights = rates[:6]**(-.7)
    weights /= weights.sum()
    factor_cov = np.repeat(np.repeat(np.array([[1., .35], [.35, 1.]]), 6, axis=0), 6, axis=1)
    stationary = factor_cov/(rates[:, None]+rates[None, :])
    z = rng.standard_normal((samples, 12))@psd_factor(stationary).T
    y = z.reshape(samples, 2, 6)@weights
    t = rng.uniform(.05, .95, samples)
    q = rng.integers(-6, 7, (samples, 2))
    base = np.zeros(samples)
    dt = np.zeros(samples)
    grad = np.zeros((samples, 12))
    hess = np.zeros((samples, 12, 12))
    up, down = np.zeros((samples, 2)), np.zeros((samples, 2))
    reduced = np.zeros(samples)
    sigma = 1.1*np.exp(.5*(.75*y-.5*.75**2*.0776117878004893))
    for asset in range(2):
        value, first, second, temporal = [np.zeros(samples) for _ in range(4)]
        for qi in range(-6, 7):
            ix = q[:, asset] == qi
            sp = splines[qi+6]
            value[ix] = sp.ev(t[ix], y[ix, asset])
            first[ix] = sp.ev(t[ix], y[ix, asset], dy=1)
            second[ix] = sp.ev(t[ix], y[ix, asset], dy=2)
            temporal[ix] = sp.ev(t[ix], y[ix, asset], dx=1)
            up[ix, asset] = splines[min(qi+1, 6)+6].ev(t[ix], y[ix, asset])-value[ix]
            down[ix, asset] = splines[max(qi-1, -6)+6].ev(t[ix], y[ix, asset])-value[ix]
        base += value
        dt += temporal
        block = slice(asset*6, (asset+1)*6)
        grad[:, block] = first[:, None]*weights
        hess[:, block, block] = second[:, None, None]*(weights[:, None]*weights[None, :])
        reduced += temporal-1.35*y[:, asset]*first + .5*.20955182706132114*(second-.2*first*first)-.1*q[:, asset]**2*sigma[:, asset]**2
        reduced += np.where(q[:, asset] < 6, hamiltonian(up[:, asset]), 0)
        reduced += np.where(q[:, asset] > -6, hamiltonian(down[:, asset]), 0)
    cov_ab = .7*sigma[:, 0]*sigma[:, 1]
    risk = (q[:, 0]*sigma[:, 0])**2 + (q[:, 1]*sigma[:, 1])**2 + 2*q[:, 0]*q[:, 1]*cov_ab

    def full(time_derivative, gradient, hessian, gain_up, gain_down):
        result = time_derivative-np.sum(rates*z*gradient, axis=1)
        result += .5*np.einsum('ij,nij->n', factor_cov, hessian)-.1*np.einsum('ni,ij,nj->n', gradient, factor_cov, gradient)
        result -= .1*risk
        result += np.sum(np.where(q < 6, hamiltonian(gain_up), 0), axis=1)
        result += np.sum(np.where(q > -6, hamiltonian(gain_down), 0), axis=1)
        return result

    separate = full(dt, grad, hess, up, down)
    c = -.2*(1-t)*cov_ab*q[:, 0]*q[:, 1]
    a = np.tile(.375*weights, 2)
    corrected = full(dt+.2*cov_ab*q[:, 0]*q[:, 1], grad+c[:, None]*a,
                     hess+c[:, None, None]*a[:, None]*a[None, :],
                     up-.2*(1-t[:, None])*cov_ab[:, None]*q[:, ::-1],
                     down+.2*(1-t[:, None])*cov_ab[:, None]*q[:, ::-1])
    finite = np.isfinite(separate)&np.isfinite(corrected)
    interior = np.all(abs(y) < 2*np.sqrt(.0776117878004893), axis=1)
    def metric(value):
        v = value[interior]
        return {'rms': float(np.sqrt(np.mean(v*v))), 'max_abs': float(np.max(abs(v))), 'mean': float(np.mean(v))}
    out = output_dir('validation', '20261013-full-residual')
    corrected_dt=dt+.2*cov_ab*q[:,0]*q[:,1]
    corrected_grad=grad+c[:,None]*a
    corrected_hess=hess+c[:,None,None]*a[:,None]*a[None,:]
    corrected_up=up-.2*(1-t[:,None])*cov_ab[:,None]*q[:,::-1]
    corrected_down=down+.2*(1-t[:,None])*cov_ab[:,None]*q[:,::-1]
    jet_rows=[]
    for ix in range(samples):
        price_cov=np.array([[sigma[ix,0]**2,cov_ab[ix]],[cov_ab[ix],sigma[ix,1]**2]])
        for time_derivative,gradient,hessian,gain_up,gain_down,reference in [(dt[ix],grad[ix],hess[ix],up[ix],down[ix],separate[ix]),(corrected_dt[ix],corrected_grad[ix],corrected_hess[ix],corrected_up[ix],corrected_down[ix],corrected[ix])]:
            jet_rows.append(np.concatenate((q[ix],z[ix],price_cov.ravel(),[time_derivative],gradient,hessian.ravel(),gain_up,gain_down,[reference])))
    np.savetxt(out/'operator_jets.csv',jet_rows,delimiter=',',fmt='%.17g')
    np.savetxt(out/'samples.csv', np.column_stack((t, q, y, reduced, separate, corrected)), delimiter=',', header='t,qA,qB,yA,yB,reduced_sum,full_separate,full_covariance_proxy', comments='')
    report = {'seed':20261013, 'samples':samples, 'interior_samples':int(interior.sum()), 'all_finite':bool(finite.all()),
              'policy_source_sha256':p.source_sha256, 'reduced_sum':metric(reduced), 'full_separate':metric(separate), 'full_covariance_proxy':metric(corrected),
              'derivatives':'Cubic time/state spline baseline; analytic covariance gradient/Hessian and time derivative; full nonlinear arrivals and factor correlations',
              'limitations':['Derivative reconstruction is not an independently converged reference solution', 'No derivative/simulation convergence certificate', 'No fitted P3', 'Residual change is not economic objective improvement']}
    (out/'summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
