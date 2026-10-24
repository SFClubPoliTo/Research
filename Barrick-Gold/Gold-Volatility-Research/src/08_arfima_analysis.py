import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.fft import fft
from scipy.stats import norm

from config import DATA_PROCESSED_DIR, OUTPUT_DIR
from utils import save_csv, save_figure, write_text_file

def gph_long_memory_estimate(x, m=None):
    """
    Geweke-Porter-Hudak (GPH) log-periodogram estimator of the fractional
    differencing parameter d. The estimate is not restricted to the
    covariance-stationary region d < 0.5; values in [0.5, 1) indicate
    non-stationary but mean-reverting long memory.
    Returns d_hat, its regression standard error, and the bandwidth m.
    """
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    x = x - np.mean(x)
    T = len(x)

    if m is None:
        m = int(np.floor(T ** 0.5))

    if m <= 2:
        raise ValueError("m is too small for GPH estimation.")

    freqs = 2 * np.pi * np.arange(1, m + 1) / T
    fft_vals = fft(x)
    periodogram = (1 / (2 * np.pi * T)) * np.abs(fft_vals) ** 2
    I_lambda = periodogram[1:m + 1]

    y = np.log(I_lambda)
    X = -2 * np.log(2 * np.sin(freqs / 2))

    X_mat = np.column_stack((np.ones(m), X))
    beta = np.linalg.lstsq(X_mat, y, rcond=None)[0]
    residuals = y - X_mat @ beta
    sigma2 = np.sum(residuals ** 2) / (m - 2)
    XtX_inv = np.linalg.inv(X_mat.T @ X_mat)
    var_beta = sigma2 * XtX_inv

    d_hat = beta[1]
    se_d = np.sqrt(var_beta[1, 1])

    return d_hat, se_d, m


def compute_abs_returns(returns: pd.Series) -> pd.Series:
    return returns.abs()


def plot_long_acf_two_panel(
    series_gold: pd.Series,
    series_silver: pd.Series,
    max_lag: int,
    filename: str,
    ylim=(0, 0.30),
):
    """
    Plot ACF of gold and silver absolute returns in a single 2x1 figure.
    Lag 0 is excluded to avoid the trivial ACF=1 dominating the scale.
    """
    from statsmodels.tsa.stattools import acf

    gold_clean = pd.Series(series_gold).dropna()
    silver_clean = pd.Series(series_silver).dropna()

    acf_gold = acf(gold_clean, nlags=max_lag, fft=True)
    acf_silver = acf(silver_clean, nlags=max_lag, fft=True)

    lags = np.arange(1, max_lag + 1)
    acf_gold = acf_gold[1:max_lag + 1]
    acf_silver = acf_silver[1:max_lag + 1]

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    # Gold
    axes[0].vlines(lags, 0, acf_gold, color="tab:orange", linewidth=1.2)
    axes[0].scatter(lags, acf_gold, color="tab:orange", s=18)
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_ylabel("ACF")
    axes[0].set_title("ACF of gold absolute returns (lags 1–100)")
    axes[0].set_ylim(*ylim)

    # Silver
    axes[1].vlines(lags, 0, acf_silver, color="tab:green", linewidth=1.2)
    axes[1].scatter(lags, acf_silver, color="tab:green", s=18)
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_xlabel("Lag")
    axes[1].set_ylabel("ACF")
    axes[1].set_title("ACF of silver absolute returns (lags 1–100)")
    axes[1].set_ylim(*ylim)

    fig.tight_layout()
    save_figure(fig, filename)


def fractional_difference(series, d, thresh=1e-4):
    """
    Apply the truncated fractional difference (1 - L)^d to a series:
    y_t = sum_k w_k x_{t-k}, with w_0 = 1 and w_k = -w_{k-1} (d - k + 1) / k.
    Returns a pandas Series aligned on the tail of the original index.
    """
    if isinstance(series, pd.Series):
        clean = series.dropna()
        values = clean.values
        index = clean.index
    else:
        values = np.asarray(series, dtype=float)
        values = values[~np.isnan(values)]
        index = None

    w = [1.0]
    k = 1
    while True:
        w_k = -w[-1] * (d - k + 1) / k
        if abs(w_k) < thresh:
            break
        w.append(w_k)
        k += 1

    # np.convolve already reverses the kernel, so the weights are passed in
    # natural order: w_0 multiplies the most recent observation x_t.
    w = np.array(w)
    fdiff = np.convolve(values, w, mode="valid")

    if index is not None:
        fd_index = index[len(index) - len(fdiff):]
        return pd.Series(fdiff, index=fd_index)
    return pd.Series(fdiff)


def check_fractional_difference():
    """Self-check: d = 1 must reproduce x_t - x_{t-1} and d = 0 the identity."""
    x = np.array([1.0, 4.0, 2.0, 7.0, 3.0, 5.0])
    assert np.allclose(fractional_difference(x, 1.0).values, np.diff(x)), "d=1 is not the first difference"
    assert np.allclose(fractional_difference(x, 0.0).values, x), "d=0 is not the identity"


def gph_tests(d_hat: float, se_d: float) -> dict:
    """Two-sided t-tests of H0: d = 0, 0.5, 1 using the GPH regression standard error."""
    out = {}
    for label, d0 in [("0", 0.0), ("05", 0.5), ("1", 1.0)]:
        t_stat = (d_hat - d0) / se_d
        out[f"t_d{label}"] = t_stat
        out[f"p_d{label}"] = 2 * norm.sf(abs(t_stat))
    return out


def describe_gph_tests(df: pd.DataFrame, alpha: float = 0.05) -> str:
    parts = []
    for label, d0 in [("0", "0"), ("05", "0.5"), ("1", "1")]:
        rejected = (df[f"p_d{label}"] < alpha).all()
        not_rejected = (df[f"p_d{label}"] >= alpha).all()
        if rejected:
            parts.append(f"$d={d0}$ is rejected for both assets")
        elif not_rejected:
            parts.append(f"$d={d0}$ is not rejected for either asset")
        else:
            parts.append(f"$d={d0}$ is rejected for one asset only")
    return "At the 5\\% level, " + "; ".join(parts) + "."


def build_latex_table(df: pd.DataFrame) -> str:
    latex = (
        "\\begin{table}[H]\n"
        "  \\centering\n"
        "  \\caption{GPH estimates of the fractional differencing parameter $d$ for absolute returns of gold and silver}\n"
        "  \\label{tab:arfima-gph}\n"
        "  \\begin{tabular}{lcccccc}\n"
        "    \\toprule\n"
        "    Asset & $m$ & $\\hat{d}$ & s.e.($\\hat{d}$) & $t$($d=0$) & $t$($d=0.5$) & $t$($d=1$) \\\\\n"
        "    \\midrule\n"
    )

    for _, row in df.iterrows():
        latex += (
            f"    {row['asset']} & "
            f"{int(row['m'])} & "
            f"{row['d_hat']:.3f} & "
            f"{row['se_d']:.3f} & "
            f"{row['t_d0']:.2f} ({row['p_d0']:.3f}) & "
            f"{row['t_d05']:.2f} ({row['p_d05']:.3f}) & "
            f"{row['t_d1']:.2f} ({row['p_d1']:.3f}) \\\\\n"
        )

    if (df["d_hat"] >= 0.5).all():
        location = (
            "Both point estimates exceed 0.5, i.e. they lie in the non-stationary, mean-reverting range, "
            "which is consistent with fractionally differencing the series before further modelling. "
        )
    elif (df["d_hat"] < 0.5).all():
        location = "Both point estimates lie in the covariance-stationary long-memory range. "
    else:
        location = "The point estimates straddle the stationarity boundary $d=0.5$. "

    latex += (
        "    \\bottomrule\n"
        "  \\end{tabular}\n"
        "  \\vspace{0.2cm}\n"
        "  \\begin{minipage}{0.9\\textwidth}\n"
        "  \\footnotesize\n"
        "  \\textit{Notes}: The table reports Geweke--Porter--Hudak log-periodogram estimates "
        "of the fractional differencing parameter $d$ for the series of absolute daily log returns "
        "on GLD and SLV (in percentage points), using the first $m = \\lfloor T^{0.5} \\rfloor$ Fourier "
        "frequencies. Columns $t$($d=d_0$) report $(\\hat{d}-d_0)/\\mathrm{s.e.}(\\hat{d})$ with two-sided "
        "normal $p$-values in parentheses. Values $0 < d < 0.5$ correspond to covariance-stationary long "
        "memory and $0.5 \\le d < 1$ to non-stationary but mean-reverting long memory. "
        f"{location}{describe_gph_tests(df)} "
        "This is a semiparametric fractional-differencing analysis; no parametric ARFIMA model is estimated.\n"
        "  \\end{minipage}\n"
        "\\end{table}\n"
    )
    return latex


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    returns = pd.read_csv(
        DATA_PROCESSED_DIR / "asset_returns.csv",
        index_col=0,
        parse_dates=True
    )

    gold_ret = returns["gold"].dropna()
    silver_ret = returns["silver"].dropna()

    abs_gold = compute_abs_returns(gold_ret) * 100
    abs_silver = compute_abs_returns(silver_ret) * 100

    abs_desc = pd.concat(
        [
            abs_gold.describe().to_frame("gold_abs_ret"),
            abs_silver.describe().to_frame("silver_abs_ret"),
        ],
        axis=1
    )
    save_csv(abs_desc, "arfima_abs_returns_describe.csv")

    d_gold, se_gold, m_gold = gph_long_memory_estimate(abs_gold.values)
    d_silver, se_silver, m_silver = gph_long_memory_estimate(abs_silver.values)

    arfima_df = pd.DataFrame(
        [
            {"asset": "Gold", "m": m_gold, "d_hat": d_gold, "se_d": se_gold, **gph_tests(d_gold, se_gold)},
            {"asset": "Silver", "m": m_silver, "d_hat": d_silver, "se_d": se_silver, **gph_tests(d_silver, se_silver)},
        ]
    )
    # Asymptotic GPH standard error pi / sqrt(24 m), reported for comparison only.
    arfima_df["se_d_asymptotic"] = np.pi / np.sqrt(24 * arfima_df["m"])

    save_csv(arfima_df, "arfima_gph_long_memory.csv", index=False)

    latex = build_latex_table(arfima_df)
    write_text_file(latex, "arfima_gph_table.tex", subdir="tables")

    plot_long_acf_two_panel(
        abs_gold,
        abs_silver,
        max_lag=100,
        filename="acf_abs_returns_gold_silver.png",
        ylim=(0, 0.30),
    )

    # Fractionally differenced series
    check_fractional_difference()
    fd_gold = fractional_difference(abs_gold, d_gold)
    fd_silver = fractional_difference(abs_silver, d_silver)

    fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    abs_gold.tail(1000).plot(ax=ax[0], color="tab:blue", linewidth=0.8)
    ax[0].set_title("Gold absolute returns (in %)")
    ax[0].set_ylabel("|r_t|")

    fd_gold.tail(1000).plot(ax=ax[1], color="tab:orange", linewidth=0.8)
    ax[1].set_title(f"Fractionally differenced gold series with d = {d_gold:.3f}")
    ax[1].set_ylabel("FD(|r_t|)")

    fig.tight_layout()
    save_figure(fig, "arfima_fd_gold.png")

    fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    abs_silver.tail(1000).plot(ax=ax[0], color="tab:blue", linewidth=0.8)
    ax[0].set_title("Silver absolute returns (in %)")
    ax[0].set_ylabel("|r_t|")

    fd_silver.tail(1000).plot(ax=ax[1], color="tab:green", linewidth=0.8)
    ax[1].set_title(f"Fractionally differenced silver series with d = {d_silver:.3f}")
    ax[1].set_ylabel("FD(|r_t|)")

    fig.tight_layout()
    save_figure(fig, "arfima_fd_silver.png")

    print("\nFractional differencing / GPH results:")
    print(arfima_df)


if __name__ == "__main__":
    main()