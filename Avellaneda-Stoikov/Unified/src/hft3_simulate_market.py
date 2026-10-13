"""Illustrative scalar-policy trading sessions; not a corrected-policy benchmark.

Frozen price/volatility per step, Poisson thinning with sequential inventory
updates; OU factors are exact on the time grid. No fees beyond terminal cost.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'hft3' / 'market_sessions'
FIG = ROOT / 'outputs' / 'img' / 'publication' / 'hft3'
OUT.mkdir(exist_ok=True)
VAR = .0776117878004893
BASE = np.log1p(.2 / 1.15) / .2


from hft3_policy import Policy


def simulate(policy, environment, paths=300, steps=3900, seed=42):
    rng = np.random.default_rng(seed)
    dt = 1/steps
    rates = np.geomspace(3, 180, 6)
    weights = rates**(-.7)
    weights /= weights.sum()
    sums = rates[:, None]+rates[None, :]
    cov = 1/sums
    innovation_cov = -np.expm1(-sums*dt)/sums
    eigenvalues, eigenvectors = np.linalg.eigh(innovation_cov)
    # Small-step common-noise covariance is nearly singular in float64.
    assert eigenvalues.min() >= -1e-12*eigenvalues.max()
    chol = eigenvectors @ np.diag(np.sqrt(np.maximum(eigenvalues, 0)))
    covariance_error = float(np.max(abs(chol@chol.T-innovation_cov)))
    z = rng.standard_normal((paths, 6)) @ np.linalg.cholesky(cov).T
    y = z @ weights if environment == 'E2' else rng.normal(0, np.sqrt(VAR), paths)
    price = np.full(paths, 100.)
    q = np.zeros((2, paths), dtype=int)
    cash = np.zeros((2, paths))
    trace = []
    fills = np.zeros((2, paths), dtype=int)
    max_accounting_error = 0.
    for n in range(steps):
        t = n*dt
        sigma = 1.1*np.exp(.5*(.75*y-.5*.75**2*VAR))
        bid, ask = policy.offsets(t, q[1], y)
        trace.append([t, price[0], y[0], sigma[0], price[0]-bid[0], price[0]+ask[0], q[0, 0], q[1, 0], cash[0, 0]+q[0, 0]*price[0], cash[1, 0]+q[1, 0]*price[0]])
        # Common candidate arrivals, sides and acceptance uniforms for both policies.
        counts = rng.poisson(28*dt, paths)
        for event in range(int(counts.max())):
            buy = rng.random(paths) < .5  # dealer buys at its bid
            uniform = rng.random(paths)
            for strategy in range(2):
                if strategy == 0:
                    b = np.where(q[0] < 6, BASE, np.nan)
                    a = np.where(q[0] > -6, BASE, np.nan)
                else:
                    b, a = policy.offsets(t, q[1], y)
                offset = np.where(buy, b, a)
                active = (counts > event) & (uniform < np.exp(-1.15*offset))
                delta_q = np.where(active, np.where(buy, 1, -1), 0)
                before = cash[strategy]+q[strategy]*price
                cash[strategy] += -delta_q*price + np.where(active, offset, 0.)
                q[strategy] += delta_q
                after = cash[strategy]+q[strategy]*price
                max_accounting_error = max(max_accounting_error, float(np.max(abs(after-before-np.where(active, offset, 0.)))))
                fills[strategy] += active
        assert np.all(abs(q) <= 6)
        price += sigma*np.sqrt(dt)*rng.standard_normal(paths)
        if environment == 'E2':
            z = z*np.exp(-rates*dt) + rng.standard_normal((paths, 6)) @ chol.T
            y = z @ weights
        else:
            y = y*np.exp(-1.35*dt) + np.sqrt(VAR*(-np.expm1(-2*1.35*dt)))*rng.standard_normal(paths)
    sigma = 1.1*np.exp(.5*(.75*y-.5*.75**2*VAR))
    wealth = cash+q*price
    cost = (.6+.28*sigma)*abs(q)+.18*q*q
    pnl = wealth-cost
    trace.append([1., price[0], y[0], sigma[0], np.nan, np.nan, q[0, 0], q[1, 0], wealth[0, 0], wealth[1, 0]])
    terminal_q = q.copy()
    cash = pnl.copy()
    q[:] = 0
    assert np.all(q == 0) and max_accounting_error < 1e-10
    tr = np.asarray(trace)
    np.savetxt(OUT/f'{environment}_session.csv', tr, delimiter=',', header='t,price,y,sigma,bid_p2,ask_p2,q_naive,q_p2,wealth_naive,wealth_p2', comments='')
    np.savetxt(OUT/f'{environment}_terminal.csv', np.column_stack((pnl.T, terminal_q.T, cost.T, fills.T)), delimiter=',', header='pnl_naive,pnl_p2,q_pre_naive,q_pre_p2,cost_naive,cost_p2,fills_naive,fills_p2', comments='')
    fig, ax = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    ax[0, 0].plot(tr[:, 0], tr[:, 1], color='.3', label='Mid-price')
    ax[0, 0].plot(tr[:, 0], tr[:, 4], color='green', lw=.8, label='P2 bid')
    ax[0, 0].plot(tr[:, 0], tr[:, 5], color='green', ls='--', lw=.8, label='P2 ask')
    ax[0, 0].set(title='(a) Solved scalar policy on a price path', ylabel='Price units')
    bins = np.linspace(pnl.min(), pnl.max(), 26)
    for s, (name, color) in enumerate((('Naive', 'tab:blue'), ('Scalar HJB P2', 'green'))):
        ax[0, 1].step(tr[:, 0], tr[:, 6+s], where='post', color=color, label=name)
        ax[0, 1].plot([1, 1], [terminal_q[s, 0], 0], ':', color=color)
        ax[1, 0].plot(tr[:, 0], tr[:, 8+s], color=color, label=name)
        ax[1, 0].scatter([1], [pnl[s, 0]], color=color, marker='x')
        ax[1, 1].hist(pnl[s], bins=bins, histtype='step', color=color, label=name, linewidth=1.5)
    ax[0, 1].set(title='(b) Inventory and terminal close-out', ylabel='Unit orders')
    ax[1, 0].set(title='(c) Mark-to-market wealth; x = liquidated PnL', ylabel='Monetary units')
    ax[1, 1].set(title=f'(d) Liquidated PnL, {paths} paths', xlabel='Monetary units', ylabel='Count')
    for axis in ax.flat:
        axis.grid(alpha=.2)
        axis.legend(fontsize=8)
    for axis in (ax[0, 0], ax[0, 1], ax[1, 0]):
        axis.set_xlabel('Normalized time')
    fig.suptitle(f'{environment}: '+('six-factor lifted market' if environment == 'E2' else 'scalar OU market')+' | seed 42, path 0')
    fig.savefig(FIG/f'market_session_{environment}.png', dpi=180)
    plt.close(fig)
    difference = pnl[1]-pnl[0]
    return dict(environment=environment, paths=paths, steps=steps, seed=seed, innovation_covariance_reconstruction_error=covariance_error, minimum_covariance_eigenvalue=float(eigenvalues.min()), accounting_error=max_accounting_error, mean_pnl=pnl.mean(axis=1).tolist(), mean_abs_preclose_inventory=np.mean(abs(terminal_q), axis=1).tolist(), mean_paired_pnl_difference=float(difference.mean()), paired_standard_error=float(difference.std(ddof=1)/np.sqrt(paths)))


if __name__ == '__main__':
    plt.rcParams.update({'font.family': 'serif', 'font.size': 10})
    policy = Policy()
    # At time/state nodes, interpolation reproduces the exported theta differences.
    for k in (0, 20, 40):
        q = np.arange(-6, 7)
        y = np.full(13, policy.y[120])
        b, a = policy.offsets(policy.times[k], q, y)
        expected = np.clip(BASE-np.diff(policy.value[k, :, 120]), .02, 4)
        assert np.allclose(b[:-1], expected, atol=1e-12)
        assert np.isnan(b[-1]) and np.isnan(a[0])
    results = [simulate(policy, env) for env in ('E1', 'E2')]
    report = dict(results=results, out_of_domain_lookup_count=policy.clamps, status='Illustrative baseline application; time-step convergence and independent residual not certified; no P3 or latency comparison', policy='Linear theta interpolation in t/Y, q discrete; gains then bounded Hamiltonian; state clamped at domain edge with count')
    (OUT/'summary.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
