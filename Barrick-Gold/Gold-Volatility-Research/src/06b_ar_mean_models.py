import numpy as np
import pandas as pd
import statsmodels.api as sm

from config import DATA_PROCESSED_DIR
from utils import newey_west_maxlags, save_csv, write_text_file


P_MAX = 10


def build_ar_dataset(series: pd.Series, p: int, p_max: int = P_MAX) -> pd.DataFrame:
    """
    Build the AR(p) design on a common estimation sample: the first p_max
    observations are dropped for every p, so that AIC/BIC are comparable
    across lag orders (identical nobs).
    """
    df = pd.DataFrame({"y": series})
    for lag in range(1, p + 1):
        df[f"lag{lag}"] = series.shift(lag)
    return df.iloc[p_max:].dropna()


def fit_ar_ols(series: pd.Series, p: int, p_max: int = P_MAX):
    df = build_ar_dataset(series, p, p_max)
    y = df["y"]
    X = df.drop(columns="y")
    X.insert(0, "const", 1.0)
    model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": newey_west_maxlags(len(y))})
    return model, df


def select_ar_order(series: pd.Series, p_max: int = P_MAX):
    rows = []
    for p in range(0, p_max + 1):
        model, _ = fit_ar_ols(series, p, p_max)
        rows.append(
            {
                "p": p,
                "AIC": model.aic,
                "BIC": model.bic,
                # R2 of the constant-only model is zero by construction.
                "R2": model.rsquared if p > 0 else 0.0,
                "nobs": int(model.nobs),
            }
        )
    sel = pd.DataFrame(rows)
    assert sel["nobs"].nunique() == 1, "AR(p) candidates must share a common sample"
    p_aic = int(sel.loc[sel["AIC"].idxmin(), "p"])
    p_bic = int(sel.loc[sel["BIC"].idxmin(), "p"])
    return sel, p_aic, p_bic


def joint_f_test_all_lags(model, p: int):
    if p == 0:
        # AR(0) (constant only) has no lag coefficients to test.
        return np.nan, np.nan
    restriction = ", ".join([f"lag{i} = 0" for i in range(1, p + 1)])
    ftest = model.f_test(restriction)
    return float(ftest.fvalue), float(ftest.pvalue)


def build_latex_arp_table(df: pd.DataFrame) -> str:
    d = df.copy()
    for col in ["R2_AIC", "R2_BIC", "F_AIC", "F_pvalue_AIC", "F_BIC", "F_pvalue_BIC"]:
        d[col] = d[col].astype(float)

    latex = d.to_latex(
        index=False,
        float_format="%.4f",
        na_rep="--",
    )

    wrapped = (
        "\\begin{table}[H]\n"
        "\\centering\n"
        "\\caption{AR($p$) order selection and joint significance tests "
        "for daily gold and silver returns, 2006--2024}\n"
        "\\label{tab:arp-selection}\n"
        f"{latex}\n"
        "\\vspace{0.2cm}\n"
        "\\begin{minipage}{0.9\\textwidth}\n"
        "\\footnotesize\n"
        "\\textit{Notes}: Daily log returns on GLD and SLV. "
        "For each asset, $p_{AIC}$ and $p_{BIC}$ denote the lag order minimizing "
        "Akaike and Bayesian information criteria over $p \\in \\{0,1,\\dots,10\\}$, where $p=0$ "
        "is the constant-only (white-noise) model. All candidates are estimated by OLS on a common "
        "sample that drops the first 10 observations, so information criteria are comparable. "
        "$F$ denotes the joint Wald F-test, based on Newey--West HAC covariance, of the null hypothesis "
        "that all lag coefficients are zero in the selected AR($p$) specification; it is not defined "
        "(--) when $p=0$ is selected.\n"
        "\\end{minipage}\n"
        "\\end{table}\n"
    )
    return wrapped


def main():
    returns = pd.read_csv(
        DATA_PROCESSED_DIR / "asset_returns.csv",
        index_col=0,
        parse_dates=True,
    )
    data = returns.dropna().copy()

    results_summary = []
    selection_tables = {}

    for asset in ["gold", "silver"]:
        series = data[asset]

        sel_table, p_aic, p_bic = select_ar_order(series, p_max=P_MAX)
        selection_tables[asset] = sel_table

        model_aic, _ = fit_ar_ols(series, p_aic, P_MAX)
        model_bic, _ = fit_ar_ols(series, p_bic, P_MAX)

        f_aic, pval_aic = joint_f_test_all_lags(model_aic, p_aic)
        f_bic, pval_bic = joint_f_test_all_lags(model_bic, p_bic)

        results_summary.append(
            {
                "Asset": asset.capitalize(),
                "p_AIC": p_aic,
                "p_BIC": p_bic,
                "R2_AIC": float(sel_table.set_index("p").loc[p_aic, "R2"]),
                "R2_BIC": float(sel_table.set_index("p").loc[p_bic, "R2"]),
                "F_AIC": f_aic,
                "F_pvalue_AIC": pval_aic,
                "F_BIC": f_bic,
                "F_pvalue_BIC": pval_bic,
            }
        )

        # Salva tabella di selezione dettagliata per asset (csv)
        save_csv(sel_table, f"arp_order_selection_{asset}.csv", index=False)

    arp_summary = pd.DataFrame(results_summary)
    save_csv(arp_summary, "arp_summary_returns.csv", index=False)

    latex_table = build_latex_arp_table(arp_summary)
    write_text_file(latex_table, "arp_selection_returns.tex", subdir="tables")

    print("\n=== AR(p) order selection summary ===")
    print(arp_summary)


if __name__ == "__main__":
    main()