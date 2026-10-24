import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from arch import arch_model
from statsmodels.stats.diagnostic import acorr_ljungbox

from config import DATA_PROCESSED_DIR, OUTPUT_DIR
from utils import save_csv, save_figure, write_text_file

LJUNG_BOX_LAGS = [10, 20]

GARCH_SPECS = [
    ("GARCH(1,1)-N", 0, "normal"),
    ("GARCH(1,1)-t", 0, "t"),
    ("GJR-GARCH(1,1,1)-t", 1, "t"),
]


def fit_garch_11(series: pd.Series, o: int = 0, dist: str = "normal"):
    model = arch_model(
        series,
        mean="constant",
        vol="GARCH",
        p=1,
        o=o,
        q=1,
        dist=dist,
        rescale=False,
    )
    result = model.fit(update_freq=50, disp="off")
    return result


def garch_comparison_row(res, asset: str, model_name: str) -> dict:
    """Parameters, persistence, fit, and Ljung-Box diagnostics on standardized residuals."""
    params = res.params
    alpha = params["alpha[1]"]
    beta = params["beta[1]"]
    gamma = params.get("gamma[1]", 0.0)
    # With symmetric innovations, P(eps < 0) = 1/2, so persistence = alpha + gamma/2 + beta.
    persistence = alpha + 0.5 * gamma + beta

    row = {
        "asset": asset,
        "model": model_name,
        "mu": params["mu"],
        "omega": params["omega"],
        "alpha": alpha,
        "gamma": params.get("gamma[1]", np.nan),
        "se_gamma": res.std_err.get("gamma[1]", np.nan),
        "beta": beta,
        "nu": params.get("nu", np.nan),
        "persistence": persistence,
        "loglikelihood": res.loglikelihood,
        "aic": res.aic,
        "bic": res.bic,
        "nobs": int(res.nobs),
    }

    std_resid = pd.Series(res.std_resid).dropna()
    lb = acorr_ljungbox(std_resid, lags=LJUNG_BOX_LAGS, return_df=True)
    lb_sq = acorr_ljungbox(std_resid ** 2, lags=LJUNG_BOX_LAGS, return_df=True)
    for lag in LJUNG_BOX_LAGS:
        row[f"lb_z_Q{lag}"] = lb.loc[lag, "lb_stat"]
        row[f"lb_z_pvalue{lag}"] = lb.loc[lag, "lb_pvalue"]
        row[f"lb_z2_Q{lag}"] = lb_sq.loc[lag, "lb_stat"]
        row[f"lb_z2_pvalue{lag}"] = lb_sq.loc[lag, "lb_pvalue"]
    return row


def build_latex_garch_comparison_table(df: pd.DataFrame) -> str:
    def fmt(x, digits=3):
        return f"{x:.{digits}f}" if pd.notna(x) else "--"

    latex = (
        "\\begin{table}[H]\n"
        "\\centering\n"
        "\\caption{GARCH(1,1), Student-$t$ GARCH(1,1), and GJR-GARCH(1,1,1)-$t$ estimates "
        "with residual diagnostics for gold and silver daily returns}\n"
        "\\label{tab:garch-comparison}\n"
        "\\resizebox{\\textwidth}{!}{%\n"
        "\\begin{tabular}{llccccccccc}\n"
        "\\toprule\n"
        "Asset & Model & $\\hat{\\alpha}$ & $\\hat{\\gamma}$ & $\\hat{\\beta}$ & $\\hat{\\nu}$ & "
        "Persistence & Log-lik. & BIC & LB$_{10}(z)$ $p$ & LB$_{10}(z^2)$ $p$ \\\\\n"
        "\\midrule\n"
    )
    for _, row in df.iterrows():
        latex += (
            f"{row['asset']} & {row['model']} & {fmt(row['alpha'], 4)} & {fmt(row['gamma'], 4)} & "
            f"{fmt(row['beta'], 4)} & {fmt(row['nu'], 2)} & {fmt(row['persistence'], 4)} & "
            f"{fmt(row['loglikelihood'], 1)} & {fmt(row['bic'], 1)} & "
            f"{fmt(row['lb_z_pvalue10'])} & {fmt(row['lb_z2_pvalue10'])} \\\\\n"
        )
    latex += (
        "\\bottomrule\n"
        "\\end{tabular}%\n"
        "}\n"
        "\\vspace{0.2cm}\n"
        "\\begin{minipage}{0.9\\textwidth}\n"
        "\\footnotesize\n"
        "\\textit{Notes}: Returns in percentage points, constant mean. $\\hat{\\gamma}$ is the GJR "
        "leverage coefficient on negative shocks and $\\hat{\\nu}$ the Student-$t$ degrees of freedom. "
        "Persistence is $\\hat{\\alpha}+\\hat{\\gamma}/2+\\hat{\\beta}$. LB$_{10}(z)$ and LB$_{10}(z^2)$ "
        "report Ljung--Box $p$-values at 10 lags for standardized residuals and squared standardized "
        "residuals (lag-20 statistics are in the CSV output). The conditional-volatility figures and "
        "variance forecasts are based on the Gaussian GARCH(1,1) specification.\n"
        "\\end{minipage}\n"
        "\\end{table}\n"
    )
    return latex


def garch_params_summary(res, name: str):
    params = res.params
    se = res.std_err

    mu = params["mu"]
    omega = params["omega"]
    alpha = params["alpha[1]"]
    beta = params["beta[1]"]
    ab_sum = alpha + beta

    sigma2_inf = np.nan
    if ab_sum < 1:
        sigma2_inf = omega / (1 - ab_sum)

    return {
        "asset": name,
        "mu": mu,
        "se_mu": se["mu"],
        "omega": omega,
        "se_omega": se["omega"],
        "alpha": alpha,
        "se_alpha": se["alpha[1]"],
        "beta": beta,
        "se_beta": se["beta[1]"],
        "alpha_plus_beta": ab_sum,
        "sigma2_inf": sigma2_inf,
        "aic": res.aic,
        "bic": res.bic,
        "loglikelihood": res.loglikelihood,
        "nobs": int(res.nobs),
    }


def build_latex_garch_table(df: pd.DataFrame) -> str:
    display = df.copy()

    for col in ["mu", "omega", "alpha", "beta", "alpha_plus_beta", "sigma2_inf"]:
        display[col] = display[col].map(lambda x: f"{x:.4f}" if pd.notna(x) else "")

    latex = (
        "\\begin{table}[H]\n"
        "\\centering\n"
        "\\caption{GARCH(1,1) estimates for gold and silver daily returns}\n"
        "\\label{tab:garch-params}\n"
        "\\begin{tabular}{lcccccc}\n"
        "\\toprule\n"
        "Asset & $\\hat{\\mu}$ & $\\hat{\\omega}$ & $\\hat{\\alpha}$ & $\\hat{\\beta}$ & "
        "$\\hat{\\alpha}+\\hat{\\beta}$ & $\\hat{\\sigma}^2_{\\infty}$ \\\\\n"
        "\\midrule\n"
    )

    for _, row in display.iterrows():
        latex += (
            f"{row['asset']} & {row['mu']} & {row['omega']} & {row['alpha']} & "
            f"{row['beta']} & {row['alpha_plus_beta']} & {row['sigma2_inf']} \\\\\n"
        )

    latex += (
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\vspace{0.2cm}\n"
        "\\begin{minipage}{0.9\\textwidth}\n"
        "\\footnotesize\n"
        "\\textit{Notes}: Returns are expressed in percentage points. "
        "$\\hat{\\sigma}^2_{\\infty} = \\hat{\\omega}/(1-\\hat{\\alpha}-\\hat{\\beta})$ "
        "when $\\hat{\\alpha}+\\hat{\\beta}<1$.\n"
        "\\end{minipage}\n"
        "\\end{table}\n"
    )

    return latex


def save_returns_and_vol_plot(
    returns_series,
    cond_vol_series,
    asset_name: str,
    filename: str,
    n_obs: int = 1000
):
    color_map = {
        "Gold": "tab:orange",
        "Silver": "tab:green",
    }

    color = color_map.get(asset_name, "tab:blue")

    fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    returns_series.tail(n_obs).plot(ax=ax[0], color="tab:blue", linewidth=0.8)
    ax[0].set_title(f"{asset_name} daily returns (in %)")
    ax[0].set_ylabel("Return")

    cond_vol_series.tail(n_obs).plot(ax=ax[1], color=color, linewidth=1.0)
    ax[1].set_title(f"{asset_name} GARCH(1,1) conditional volatility")
    ax[1].set_ylabel("Volatility (std. dev., %)")

    fig.tight_layout()
    save_figure(fig, filename)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    returns = pd.read_csv(DATA_PROCESSED_DIR / "asset_returns.csv", index_col=0, parse_dates=True)

    ret_gold = returns["gold"].dropna() * 100
    ret_silver = returns["silver"].dropna() * 100

    gold_desc = ret_gold.describe().to_frame(name="gold")
    silver_desc = ret_silver.describe().to_frame(name="silver")
    desc = pd.concat([gold_desc, silver_desc], axis=1)
    save_csv(desc, "garch_input_returns_describe.csv")

    res_gold = fit_garch_11(ret_gold)
    res_silver = fit_garch_11(ret_silver)

    print(res_gold.summary())
    print(res_silver.summary())

    summary_rows = [
        garch_params_summary(res_gold, "Gold"),
        garch_params_summary(res_silver, "Silver"),
    ]
    params_df = pd.DataFrame(summary_rows)

    save_csv(params_df, "garch_params.csv", index=False)

    latex_table = build_latex_garch_table(params_df[[
        "asset", "mu", "omega", "alpha", "beta", "alpha_plus_beta", "sigma2_inf"
    ]])

    write_text_file(latex_table, "garch_params.tex", subdir="tables")

    # Fat-tailed and asymmetric alternatives with residual diagnostics.
    comparison_rows = []
    for asset, series in [("Gold", ret_gold), ("Silver", ret_silver)]:
        for model_name, o, dist in GARCH_SPECS:
            res = fit_garch_11(series, o=o, dist=dist)
            comparison_rows.append(garch_comparison_row(res, asset, model_name))
    comparison_df = pd.DataFrame(comparison_rows)
    save_csv(comparison_df, "garch_model_comparison.csv", index=False)
    write_text_file(
        build_latex_garch_comparison_table(comparison_df),
        "garch_model_comparison.tex",
        subdir="tables",
    )
    print("\nGARCH model comparison:")
    print(comparison_df)

    cond_vol_gold = res_gold.conditional_volatility
    cond_vol_silver = res_silver.conditional_volatility

    cond_vol_df = pd.DataFrame({
        "gold_cond_vol": cond_vol_gold,
        "silver_cond_vol": cond_vol_silver,
    })
    save_csv(cond_vol_df, "garch_conditional_volatility.csv")

    horizon = 10
    forecasts_gold = res_gold.forecast(horizon=horizon)
    forecasts_silver = res_silver.forecast(horizon=horizon)

    fvar_gold = forecasts_gold.variance.iloc[-1].values
    fvar_silver = forecasts_silver.variance.iloc[-1].values

    forecast_df = pd.DataFrame({
        "horizon": np.arange(1, horizon + 1),
        "gold_variance_forecast": fvar_gold,
        "silver_variance_forecast": fvar_silver,
    })
    save_csv(forecast_df, "garch_variance_forecasts.csv", index=False)

    print("1- to 10-step ahead variance forecasts for gold:", fvar_gold)
    print("1- to 10-step ahead variance forecasts for silver:", fvar_silver)

    save_returns_and_vol_plot(
        ret_gold,
        cond_vol_gold,
        asset_name="Gold",
        filename="garch_condvol_gold.png",
        n_obs=1000
    )

    save_returns_and_vol_plot(
        ret_silver,
        cond_vol_silver,
        asset_name="Silver",
        filename="garch_condvol_silver.png",
        n_obs=1000
    )


if __name__ == "__main__":
    main()