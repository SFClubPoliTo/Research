"""Two synthetic assets, six OU factors each; separable P2 vs covariance proxy.

No market data, fitted residual correction, calibrated correlation or speed claim.
"""
import json
import numpy as np
from hft3_simulate_market import Policy, ROOT, FIG, VAR, plt
from hft3_multiasset_model import covariance, portfolio_variance, shifts, psd_factor, self_test

OUT = ROOT/'outputs'/'hft3'/'multiasset'
OUT.mkdir(exist_ok=True)
NAMES = ('Separate P2', 'P2 + covariance proxy')
COLORS = ('tab:blue', 'tab:purple')


def run(policy, steps=3900, paths=400, rho=.7, seed=73, figures=True):
    rng = np.random.default_rng(seed)
    dt = 1/steps
    rates = np.tile(np.geomspace(3, 180, 6), 2)
    weights = rates[:6]**(-.7)
    weights /= weights.sum()
    # Two Brownian volatility drivers, correlation .35; common within each lift.
    vol_corr = np.array([[1., .35], [.35, 1.]])
    driver_cov = np.repeat(np.repeat(vol_corr, 6, axis=0), 6, axis=1)
    sums = rates[:, None]+rates[None, :]
    stationary = driver_cov/sums
    innovation = driver_cov*(-np.expm1(-sums*dt))/sums
    factor = psd_factor(innovation)
    z = rng.standard_normal((paths, 12))@psd_factor(stationary).T
    price_corr = np.array([[1., rho], [rho, 1.]])
    price_factor = psd_factor(price_corr)
    price = np.full((paths, 2), 100.)
    q = np.zeros((2, paths, 2), dtype=int)
    q[:, :, 0] = 3  # deliberate initial long A / flat B, same for both policies
    cash = np.full((2, paths), -300.)  # zero initial marked wealth
    risk_integral = np.zeros((2, paths))
    trace, vol_trace = [], []
    fills = np.zeros((2, paths, 2), dtype=int)
    account_error = 0.
    start_clamps = policy.clamps
    for n in range(steps):
        t = n*dt
        y = z.reshape(paths, 2, 6)@weights
        sigma = 1.1*np.exp(.5*(.75*y-.5*.75**2*VAR))
        cov = covariance(sigma, price_corr)
        risk = np.array([portfolio_variance(q[s], cov) for s in range(2)])
        assert np.min(risk) >= -1e-12
        risk_integral += risk*dt
        quotes = []
        for s in range(2):
            shift = shifts(t, q[s], cov) if s else np.zeros_like(sigma)
            b, a = policy.offsets(t, q[s], y, shift)
            quotes.append((b, a))
        trace.append([t, *price[0], *q[0, 0], *q[1, 0], *risk[:, 0],
                      *(cash[:, 0]+np.sum(q[:, 0]*price[0], axis=1)),
                      *[v for s in range(2) for i in range(2) for v in (price[0, i]-quotes[s][0][0, i], price[0, i]+quotes[s][1][0, i])]])
        vol_trace.append([t, *z[0], *y[0], *sigma[0], cov[0, 0, 1]])
        # A single marked candidate stream avoids a fixed asset-order bias.
        count = rng.poisson(56*dt, paths)
        for event in range(int(count.max())):
            asset = rng.integers(0, 2, paths)
            buy = rng.random(paths) < .5
            u = rng.random(paths)
            ix = np.arange(paths)
            for s in range(2):
                shift = shifts(t, q[s], cov) if s else np.zeros_like(sigma)
                b, a = policy.offsets(t, q[s], y, shift)
                offset = np.where(buy, b[ix, asset], a[ix, asset])
                active = (count > event) & (u < np.exp(-1.15*offset))
                dq = np.where(active, np.where(buy, 1, -1), 0)
                before = cash[s]+np.sum(q[s]*price, axis=1)
                cash[s] += -dq*price[ix, asset]+np.where(active, offset, 0.)
                q[s, ix, asset] += dq
                fills[s, ix, asset] += active
                after = cash[s]+np.sum(q[s]*price, axis=1)
                account_error = max(account_error, float(np.max(abs(after-before-np.where(active, offset, 0.)))))
        assert np.all(abs(q) <= 6)
        if rho == 0:
            assert np.array_equal(q[0], q[1]) and np.array_equal(cash[0], cash[1])
        price += sigma*np.sqrt(dt)*(rng.standard_normal((paths, 2))@price_factor.T)
        z = z*np.exp(-rates*dt)+rng.standard_normal((paths, 12))@factor.T
    y = z.reshape(paths, 2, 6)@weights
    sigma = 1.1*np.exp(.5*(.75*y-.5*.75**2*VAR))
    marked = cash+np.sum(q*price, axis=2)
    costs = np.sum((.6+.28*sigma)*abs(q)+.18*q*q, axis=2)
    pnl = marked-costs
    terminal_q = q.copy()
    cash = pnl.copy()
    q[:] = 0
    assert np.all(q == 0) and account_error < 1e-10
    tr, vt = np.asarray(trace), np.asarray(vol_trace)
    tag = f'rho{rho:g}_n{steps}'
    np.savetxt(OUT/f'{tag}_session.csv', tr, delimiter=',', header='t,S_A,S_B,qA_sep,qB_sep,qA_cov,qB_cov,risk_sep,risk_cov,wealth_sep,wealth_cov,bidA_sep,askA_sep,bidB_sep,askB_sep,bidA_cov,askA_cov,bidB_cov,askB_cov', comments='')
    np.savetxt(OUT/f'{tag}_volatility.csv', vt, delimiter=',', header='t,'+','.join(f'z{i}' for i in range(12))+',yA,yB,sigmaA,sigmaB,covAB', comments='')
    np.savetxt(OUT/f'{tag}_terminal.csv', np.column_stack((pnl.T, risk_integral.T, costs.T, terminal_q.reshape(2, paths, 2)[0], terminal_q[1])), delimiter=',', header='pnl_sep,pnl_cov,int_risk_sep,int_risk_cov,cost_sep,cost_cov,qA_sep,qB_sep,qA_cov,qB_cov', comments='')
    if figures:
        fig, ax = plt.subplots(3, 2, figsize=(12, 11), constrained_layout=True)
        for i in range(2):
            ax[0, i].plot(tr[:, 0], tr[:, 1+i], color='.25', label=f'Asset {"AB"[i]} mid')
            for s in range(2):
                ax[0, i].plot(tr[:, 0], tr[:, 11+4*s+2*i], color=COLORS[s], lw=.65, label=NAMES[s]+' bid')
                ax[0, i].plot(tr[:, 0], tr[:, 12+4*s+2*i], color=COLORS[s], lw=.65, ls='--', label=NAMES[s]+' ask')
                ax[1, i].step(tr[:, 0], tr[:, 3+2*s+i], where='post', color=COLORS[s], label=NAMES[s])
                ax[1, i].plot([1, 1], [terminal_q[s, 0, i], 0], ':', color=COLORS[s])
            ax[0, i].set(title=f'Asset {"AB"[i]}: price and executable quotes', ylabel='Price units')
            ax[1, i].set(title=f'Asset {"AB"[i]}: inventory (dotted = liquidation)', ylabel='Unit orders')
        bins = np.linspace(pnl.min(), pnl.max(), 27)
        for s in range(2):
            ax[2, 0].plot(tr[:, 0], tr[:, 7+s], color=COLORS[s], label=NAMES[s])
            ax[2, 1].hist(pnl[s], bins=bins, histtype='step', color=COLORS[s], label=NAMES[s])
        ax[2, 0].set(title='Portfolio variance rate: q transpose Sigma q', ylabel='Money squared / normalized time')
        ax[2, 1].set(title=f'Liquidated portfolio PnL: {paths} paired paths', xlabel='Monetary units', ylabel='Count')
        for a in ax.flat:
            a.legend(fontsize=7)
            a.grid(alpha=.2)
        for a in ax.flat:
            if a is not ax[2, 1]:
                a.set_xlabel('Normalized time')
        fig.suptitle(f'Two synthetic assets, 6 volatility factors each; rho={rho}; seed {seed}, path 0')
        fig.savefig(FIG/'multiasset_inventory.png', dpi=180)
        plt.close(fig)
        fig, ax = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
        for i in range(2):
            for m in range(6):
                ax[0, i].plot(vt[:, 0], vt[:, 1+6*i+m], lw=.6, label=f'lambda={rates[m]:.1f}')
            ax[0, i].set(title=f'Asset {"AB"[i]}: six OU factors', ylabel='Factor state')
            ax[1, 0].plot(vt[:, 0], vt[:, 15+i], label=f'sigma {"AB"[i]}')
        ax[1, 0].set(title='Two stochastic price volatilities', ylabel='Price / sqrt(normalized time)')
        ax[1, 1].plot(vt[:, 0], vt[:, 17], color='purple', label='rho sigma_A sigma_B')
        ax[1, 1].set(title='Time-varying covariance, fixed correlation', ylabel='Price squared / normalized time')
        for a in ax.flat:
            a.set_xlabel('Normalized time')
            a.legend(fontsize=7)
            a.grid(alpha=.2)
        fig.savefig(FIG/'multiasset_volatility.png', dpi=180)
        plt.close(fig)
    def paired(v):
        d = v[1]-v[0]
        return dict(mean=float(d.mean()), se=float(d.std(ddof=1)/np.sqrt(paths)))
    return dict(rho=rho, steps=steps, paths=paths, seed=seed, mean_pnl=pnl.mean(axis=1).tolist(),
                certainty_equivalent=(-np.log(np.mean(np.exp(-.2*pnl), axis=1))/.2).tolist(),
                mean_integrated_variance=risk_integral.mean(axis=1).tolist(),
                mean_abs_preclose_inventory=np.mean(abs(terminal_q), axis=1).tolist(),
                paired_pnl=paired(pnl), paired_integrated_variance=paired(risk_integral),
                covariance_reconstruction_error=float(np.max(abs(factor@factor.T-innovation))),
                accounting_error=account_error, clamped_lookups=policy.clamps-start_clamps)


def explain_quotes(policy):
    qa = np.arange(-6, 7)
    rhos = np.linspace(-.9, .9, 91)
    grid = []
    for rho in rhos:
        q = np.column_stack((qa, np.zeros(13, dtype=int)))
        sigma = np.full(q.shape, 1.1*np.exp(-.25*.75**2*VAR))
        cov = covariance(sigma, np.array([[1., rho], [rho, 1.]]))
        _, baseline_ask = policy.offsets(.25, q, np.zeros(q.shape))
        _, ask = policy.offsets(.25, q, np.zeros(q.shape), shifts(.25, q, cov))
        grid.append(baseline_ask[:, 1]-ask[:, 1])
    fig, ax = plt.subplots(figsize=(9, 4), constrained_layout=True)
    im = ax.pcolormesh(qa, rhos, grid, shading='nearest', cmap='RdBu_r')
    fig.colorbar(im, ax=ax, label='Reduction of asset B ask (price units)')
    ax.set(xlabel='Inventory in A (B inventory = 0)', ylabel='Price correlation rho', title='Positive = willing to sell B at a lower ask; t=0.25, Y_A=Y_B=0')
    fig.savefig(FIG/'multiasset_quote_shift.png', dpi=180)
    plt.close(fig)
    np.savetxt(OUT/'ask_reduction.csv', grid, delimiter=',', header='rows rho=-.9:.02:.9; columns qA=-6:1:6; qB=0,t=.25,y=0', comments='')


if __name__ == '__main__':
    print(self_test())
    plt.rcParams.update({'font.family': 'serif', 'font.size': 9})
    policy = Policy()
    explain_quotes(policy)
    results = [run(policy), run(policy, steps=1950, figures=False),
               run(policy, steps=390, paths=20, rho=0., figures=False)]
    report = dict(results=results, asset_count=2, factors_per_asset=6,
                  price_correlation=.7, volatility_driver_correlation=.35,
                  initial_inventory=[3, 0], initial_cash=-300, price0=[100, 100],
                  correction='Frozen-covariance cross-inventory proxy on separable P2; not fitted full-HJB P3',
                  limitations=['Synthetic uncalibrated assets A/B', 'rho fixed; covariance stochastic',
                               'Two step sizes are a diagnostic, not convergence certification',
                               'No full multiasset reference HJB or residual decrease certified',
                               'Sample certainty equivalents have no confidence interval', 'No latency advantage measured'])
    (OUT/'summary.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
