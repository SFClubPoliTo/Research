"""Render the classical covariance and three-asset diagnostic panels."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def render(namespace, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    p = namespace['P']
    multi = namespace['P_MULTI']
    t = namespace['t_arr']
    prices = namespace['S_multi']
    naive = namespace['r_multi_naive']
    naive['risk'] = np.sqrt(np.maximum(np.einsum('ni,ij,nj->n', naive['inv'], namespace['Sigma_multi'], naive['inv']), 0))
    aware = namespace['r_multi_as']
    mc = namespace['mc_MULTI']
    blue, red = '#4878CF', '#C44E52'
    plt.rcParams.update({'font.family': 'serif', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.grid': True, 'grid.alpha': .3})
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.suptitle('Naive vs Inventory-Based Market Making — 3 Correlated ABM Assets, including one inverse asset', fontsize=14, fontweight='bold')
    labels = ['Asset A', 'Asset B', 'Asset C (inverse)']
    for i, label in enumerate(labels):
        axes[0, 0].plot(t, 100 * np.log(prices[:, i] / multi['S0'][i]), lw=1.1, label=label)
    axes[0, 0].set(title='(a) Asset cumulative log-returns', xlabel='Time $t$', ylabel=r'Cumulative log-return $100\log(S_t/S_0)$')
    axes[0, 0].axhline(0, color='gray', lw=.7, ls=':', alpha=.6)
    axes[0, 0].legend(fontsize=9)
    for data, color, label, style in [(naive, blue, 'Naive', '-'), (aware, red, 'Inventory-based', '--')]:
        axes[0, 1].plot(t, data['risk'], color=color, lw=1.1, ls=style, label=label)
        axes[1, 0].plot(t, data['pnl'], color=color, lw=1.1, ls=style, label=label)
    axes[0, 1].set(title='(b) Inventory Risk Path', xlabel='Time $t$', ylabel=r'Portfolio inventory risk $\|q_t\|_\Sigma$')
    axes[1, 0].set(title='(c) Mark-to-Market Portfolio PnL', xlabel='Time $t$', ylabel=r'PnL $W_t = X_t + q^\top S_t$')
    for ax in [axes[0, 1], axes[1, 0]]:
        ax.axhline(0, color='gray', lw=.7, ls=':', alpha=.6)
        ax.legend(fontsize=9)
    values = np.concatenate([mc['pnl_n'], mc['pnl_as']])
    bins = np.linspace(*np.percentile(values, [1, 99]), 55)
    for key, color, label in [('pnl_n', blue, 'Naive'), ('pnl_as', red, 'Inventory-based')]:
        axes[1, 1].hist(mc[key], bins=bins, color=color, alpha=.5, density=True, label=label)
        axes[1, 1].axvline(np.mean(mc[key]), color=color, lw=1.5, ls='--')
    axes[1, 1].set(title=f"(d) Terminal PnL ({multi['N_MC']:,} MC paths)", xlabel=r'Terminal PnL $W_T$', ylabel='Density')
    axes[1, 1].legend(fontsize=9)
    fig.tight_layout(rect=[0, 0, 1, .94])
    fig.savefig(output / 'py3.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    np.savez_compressed(output / 'py3_data.npz', time=t, prices=prices,
                        naive_risk=naive['risk'], aware_risk=aware['risk'],
                        naive_pnl=naive['pnl'], aware_pnl=aware['pnl'],
                        terminal_naive=mc['pnl_n'], terminal_aware=mc['pnl_as'])
    with plt.rc_context(matplotlib.rcParamsDefault):
        fig = plt.figure(figsize=(4.85, 4.09), dpi=100)
        ax = fig.add_axes([81/485, 79/409, 293/485, 293/409])
        im = ax.imshow(multi['corr'], cmap='coolwarm', vmin=-1, vmax=1)
        ticks = ['Asset A', 'Asset B', 'Asset C\n(inverse)']
        ax.set_xticks(range(3), ticks, rotation=35, ha='right')
        ax.set_yticks(range(3), ticks)
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{multi['corr'][i, j]:.2f}", ha='center', va='center', color='black')
        ax.set_title('Correlation Matrix')
        colorbar_ax = fig.add_axes([389/485, 79/409, 15/485, 293/409])
        fig.colorbar(im, cax=colorbar_ax, label='Correlation')
        fig.savefig(output / 'Corr.png', dpi=100)
        plt.close(fig)
