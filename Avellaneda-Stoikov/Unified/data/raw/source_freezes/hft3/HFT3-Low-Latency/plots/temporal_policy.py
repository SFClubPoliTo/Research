"""Validate exported scalar policies and plot reproducible numerical diagnostics."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'baseline_audit'
FIG = ROOT.parents[1] / 'Overleaf' / 'img'
data = np.genfromtxt(OUT / 'temporal_policy.csv', delimiter=',', names=True)
gamma, var_y = .2, .0776117878004893
sd = np.sqrt(var_y)
assert np.all(np.isfinite(data['theta']))
assert np.all(np.isnan(data['bid_offset']) == (data['q'] == 6))
assert np.all(np.isnan(data['ask_offset']) == (data['q'] == -6))
for side in ('bid_offset', 'ask_offset'):
    valid = data[side][np.isfinite(data[side])]
    assert np.all((valid >= .02) & (valid <= 4))
terminal = data[data['t'] == 1]
vol = 1.1 * np.exp(.5 * (.75 * terminal['y'] - .5 * .75**2 * var_y))
cost = (.6 + .28 * vol) * np.abs(terminal['q']) + .18 * terminal['q']**2
terminal_error = float(np.max(np.abs(terminal['theta'] + cost)))
assert terminal_error < 1e-12

def surface(domain, points, field):
    rows = data[(data['domain_sd'] == domain) & (data['points'] == points)]
    times = np.unique(rows['t'])
    ys = np.unique(rows['y'])
    values = rows[field].reshape(len(times), 13, points)[::-1]
    return times, ys, values

plt.rcParams.update({'font.family': 'serif', 'font.size': 10})
fig, axes = plt.subplots(3, 3, figsize=(12, 9), constrained_layout=True)
for col, field in enumerate(('theta', 'bid_offset', 'ask_offset')):
    ts, ys, values = surface(5, 241, field)
    for row, target in enumerate((0., .5, .975)):
        k = np.argmin(abs(ts-target))
        ax = axes[row, col]
        im = ax.pcolormesh(ys/sd, np.arange(-6, 7), values[k], shading='nearest', cmap='viridis')
        fig.colorbar(im, ax=ax)
        ax.set(title=f'{field.replace("_", " ")}, t={ts[k]:.3f}', xlabel='Y / stationary SD', ylabel='Inventory q')
fig.savefig(FIG / 'temporal_policy.png', dpi=180)
plt.close(fig)

# Compare on a common interior grid. These are differences, not exact errors.
eval_y = np.linspace(-2*sd, 2*sd, 101)
_, ref_y, ref = surface(6, 241, 'theta')
metrics = []
fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
for domain in (4, 5, 6):
    for points in (81, 161, 241):
        diffs = []
        for field in ('theta', 'bid_offset', 'ask_offset'):
            ts, y, v = surface(domain, points, field)
            _, yr, r = surface(6, 241, field)
            errors = []
            for k in range(len(ts)):
                for qi in range(13):
                    if not np.all(np.isfinite(v[k, qi])):
                        continue
                    errors.extend(abs(np.interp(eval_y, y, v[k, qi]) - np.interp(eval_y, yr, r[k, qi])))
            diffs.append(float(max(errors)))
        metrics.append(dict(domain_sd=domain, points=points, max_theta_difference=diffs[0], max_quote_difference=max(diffs[1:])))
    subset = metrics[-3:]
    for ax, key in zip(axes, ('max_theta_difference', 'max_quote_difference')):
        ax.plot([m['points'] for m in subset], [m[key] for m in subset], 'o-', label=f'Domain: {domain} SD')
        ax.set(xlabel='State grid points', ylabel='Maximum absolute difference', title=key.replace('_', ' '))
        ax.grid(alpha=.25)
        ax.legend()
fig.savefig(FIG / 'policy_sensitivity.png', dpi=180)
plt.close(fig)
(OUT / 'temporal_validation.json').write_text(json.dumps({'rows': len(data), 'terminal_error': terminal_error, 'comparison': '6 SD / 241 nodes, same 9360 time steps; |Y| <= 2 SD; all saved times and allowed q/sides; linear spatial interpolation', 'metrics': metrics, 'limitations': ['Not exact error bounds', 'Temporal refinement and independent residual validation remain open', 'No trading simulations or runtime advantage measured']}, indent=2))
print(json.dumps({'rows': len(data), 'terminal_error': terminal_error, 'metrics': metrics}, indent=2))
