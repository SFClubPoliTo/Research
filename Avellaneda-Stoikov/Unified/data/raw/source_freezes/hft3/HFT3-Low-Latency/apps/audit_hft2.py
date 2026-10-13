"""Read-only import of HFT2; export independent residual checks for C++.

Usage: python apps/audit_hft2.py --source PATH_TO_solve_rough_hjb.py
Outputs are synthetic audit data, not a calibrated backtest.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('output/baseline_audit'))
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('hft2_audit_source', args.source)
    hft2 = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = hft2
    spec.loader.exec_module(hft2)
    p = hft2.ModelParams()
    lift = hft2.build_lift(p)
    solution = hft2.solve_hjb(p, lift)
    theta = solution['theta']
    dt = p.T / p.n_steps
    dy_grid = solution['y_grid'][1] - solution['y_grid'][0]
    lam, w = lift['lam'], lift['w']
    rng = np.random.default_rng(42)
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    rows, differences, full_values, reduced_values = [], [], [], []
    gradient_terms, diffusion_terms = [], []
    for n in [0, p.n_steps//2, p.n_steps-2]:
        first, second = hft2._derivatives_y(theta[n], dy_grid)
        for q in [-p.q_max, -2, 0, 2, p.q_max]:
            qi = q+p.q_max
            for _ in range(12):
                z = lift['chol_stationary'] @ rng.standard_normal(p.lift_dim)
                y = float(w @ z)
                # Interior samples only; interpolation rule is recorded explicitly.
                if not solution['y_grid'][1] <= y <= solution['y_grid'][-2]:
                    continue
                interp = lambda a: float(np.interp(y, solution['y_grid'], a))
                value = interp(theta[n, qi])
                derivative_t = interp((theta[n+1, qi]-theta[n, qi])/dt)
                derivative_y, derivative_yy = interp(first[qi]), interp(second[qi])
                up = interp(theta[n, qi+1]) if q<p.q_max else value
                down = interp(theta[n, qi-1]) if q>-p.q_max else value
                variance = float(hft2.volatility_from_y(np.array(y), p, lift))
                arrivals = 0.
                for allowed, gain in [(q<p.q_max, up-value), (q>-p.q_max, down-value)]:
                    if allowed:
                        delta = float(np.clip(np.log1p(p.gamma/p.k)/p.gamma-gain, .02, 4.))
                        arrivals += p.A*np.exp(-p.k*delta)*(-np.expm1(-p.gamma*(delta+gain)))/p.gamma
                common = derivative_t - .5*p.gamma*q*q*variance + arrivals
                full = common - float((w*lam)@z)*derivative_y + .5*w.sum()**2*(derivative_yy-p.gamma*derivative_y**2)
                reduced = common - lift['kappa_y']*y*derivative_y + .5*lift['eta_y']**2*(derivative_yy-p.gamma*derivative_y**2)
                drift_difference = (lift['kappa_y']*y-float((w*lam)@z))*derivative_y
                diffusion_difference = .5*(w.sum()**2-lift['eta_y']**2)*(derivative_yy-p.gamma*derivative_y**2)
                np.testing.assert_allclose(full-reduced, drift_difference+diffusion_difference, atol=1e-10)
                rows.append([q, *z, variance, value, derivative_t, derivative_y, derivative_yy, up, down, full])
                differences.append(full-reduced)
                full_values.append(full); reduced_values.append(reduced)
                gradient_terms.append(drift_difference); diffusion_terms.append(diffusion_difference)
    if not rows:
        raise RuntimeError('No interior samples')
    with (out/'samples.txt').open('w', encoding='utf-8') as f:
        f.write(' '.join(map(str,lam))+'\n'+' '.join(map(str,w))+'\n')
        for row in rows:
            f.write(' '.join(map(str,row))+'\n')
    rms = lambda a: float(np.sqrt(np.mean(np.square(a))))
    summary = {
        'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
        'seed': 42, 'samples': len(rows), 'hurst': p.hurst,
        'q_max': p.q_max, 'time_indices': [0,p.n_steps//2,p.n_steps-2],
        'lift_rates': lam.tolist(), 'lift_weights': w.tolist(),
        'var_y': float(lift['var_y']), 'reduced_kappa': float(lift['kappa_y']),
        'reduced_diffusion_variance': float(lift['eta_y']**2),
        'full_aggregate_instantaneous_variance': float(w.sum()**2),
        'full_residual_rms': rms(full_values), 'reduced_residual_rms': rms(reduced_values),
        'compression_defect_rms': rms(differences),
        'drift_defect_rms': rms(gradient_terms), 'diffusion_defect_rms': rms(diffusion_terms),
        'theta_min': float(theta.min()), 'theta_max': float(theta.max()),
        'theta_at_lower_clip': int(np.count_nonzero(theta[:-1] == -60)),
        'theta_at_upper_clip': int(np.count_nonzero(theta[:-1] == 15)),
        'qualification': 'Legacy HFT2 explicit solver; forward time difference, legacy spatial differences and linear interpolation of jets. Bounded Hamiltonian [.02,4], not legacy unbounded Hamiltonian. Diagnostic only; no residual convergence or policy improvement established.'
    }
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__ == '__main__':
    main()
