import warnings
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from config import DATA_PROCESSED_DIR
from utils import save_csv, write_text_file


P_MAX = 3
Q_MAX = 3


def fit_arma_grid(series: pd.Series, p_max: int = P_MAX, q_max: int = Q_MAX) -> pd.DataFrame:
    rows = []

    for p in range(p_max + 1):
        for q in range(q_max + 1):
            # ARMA(0,0) (constant mean, white noise) is a legitimate candidate.
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = ARIMA(series, order=(p, 0, q), trend="c")
                    res = model.fit()

                rows.append(
                    {
                        "p": p,
                        "q": q,
                        "AIC": res.aic,
                        "BIC": res.bic,
                        "loglik": res.llf,
                        "nobs": int(res.nobs),
                    }
                )
            except Exception:
                continue

    if not rows:
        raise RuntimeError("No ARMA model could be estimated.")

    grid = pd.DataFrame(rows)
    # Exact Gaussian MLE uses the full sample for every order, so AIC/BIC are comparable.
    assert grid["nobs"].nunique() == 1, "ARMA candidates must share a common sample"
    return grid.sort_values(["AIC", "BIC"]).reset_index(drop=True)


def build_latex_arma_table(df: pd.DataFrame) -> str:
    latex = df.to_latex(
        index=False,
        float_format="%.4f",
        column_format="lrrrrrr",
    )

    wrapped = (
        "\\begin{table}[H]\n"
        "\\centering\n"
        "\\caption{Selected ARMA($p,q$) models for daily gold and silver returns, 2006--2024}\n"
        "\\label{tab:arma-selection}\n"
        f"{latex}\n"
        "\\vspace{0.2cm}\n"
        "\\begin{minipage}{0.9\\textwidth}\n"
        "\\footnotesize\n"
        "\\textit{Notes}: Daily log returns on GLD and SLV. "
        "For each asset, the table reports the ARMA($p,q$) specification minimizing AIC and BIC "
        "over a grid with $p,q \\in \\{0,1,2,3\\}$, including ARMA(0,0), i.e. a constant mean with "
        "white-noise errors. Models are estimated by exact Gaussian maximum likelihood using the statsmodels "
        "ARIMA implementation with $d=0$; every candidate uses the same observations, so the information "
        "criteria are directly comparable.\n"
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

    data = returns[["gold", "silver"]].dropna().copy()

    summary_rows = []

    for asset in ["gold", "silver"]:
        series = data[asset]

        grid = fit_arma_grid(series)
        save_csv(grid, f"arma_grid_{asset}.csv", index=False)

        best_aic = grid.loc[grid["AIC"].idxmin()]
        best_bic = grid.loc[grid["BIC"].idxmin()]

        summary_rows.append(
            {
                "Asset": asset.capitalize(),
                "p_AIC": int(best_aic["p"]),
                "q_AIC": int(best_aic["q"]),
                "AIC_min": float(best_aic["AIC"]),
                "p_BIC": int(best_bic["p"]),
                "q_BIC": int(best_bic["q"]),
                "BIC_min": float(best_bic["BIC"]),
            }
        )

    summary = pd.DataFrame(summary_rows)
    save_csv(summary, "arma_summary_returns.csv", index=False)

    latex_table = build_latex_arma_table(summary)
    write_text_file(latex_table, "arma_selection_returns.tex", subdir="tables")

    print("\n=== ARMA(p,q) selection summary ===")
    print(summary)


if __name__ == "__main__":
    main()