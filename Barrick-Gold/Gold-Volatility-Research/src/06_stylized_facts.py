import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import skew, kurtosis
from statsmodels.tools.sm_exceptions import InterpolationWarning
from statsmodels.tsa.stattools import acf, adfuller, kpss

from config import DATA_PROCESSED_DIR, OUTPUT_DIR
from utils import newey_west_maxlags, save_csv, write_text_file

def ar1_results(series: pd.Series):
    # Descriptive only: under a unit root the OLS t-statistic is non-standard,
    # so integration order is assessed with the ADF/KPSS tests below.
    y = series.dropna()
    y_lag = y.shift(1).dropna()
    y = y.loc[y_lag.index]

    X = sm.add_constant(y_lag)
    model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": newey_west_maxlags(len(y))})

    phi = model.params.iloc[1]
    se_phi = model.bse.iloc[1]
    t_phi = model.tvalues.iloc[1]
    r2 = model.rsquared

    return phi, se_phi, t_phi, r2


def unit_root_row(series: pd.Series, label: str, regression: str) -> dict:
    """
    ADF (H0: unit root) and KPSS (H0: stationarity around a constant/trend).
    KPSS p-values are interpolated from a table bounded at [0.01, 0.10].
    """
    x = series.dropna()
    adf_stat, adf_p, adf_lags, adf_nobs, adf_cv, _ = adfuller(x, regression=regression, autolag="AIC", result_object=False)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", InterpolationWarning)
        kpss_stat, kpss_p, kpss_lags, kpss_cv = kpss(x, regression=regression, nlags="auto", result_object=False)
    kpss_bound = ""
    if any(issubclass(w.category, InterpolationWarning) for w in caught):
        kpss_bound = "<" if kpss_p <= 0.01 else ">"

    return {
        "series": label,
        "deterministic": "constant" if regression == "c" else "constant + trend",
        "adf_stat": adf_stat,
        "adf_pvalue": adf_p,
        "adf_lags": int(adf_lags),
        "adf_cv_5pct": adf_cv["5%"],
        "kpss_stat": kpss_stat,
        "kpss_pvalue": kpss_p,
        "kpss_pvalue_bound": kpss_bound,
        "kpss_lags": int(kpss_lags),
        "kpss_cv_5pct": kpss_cv["5%"],
        "nobs": int(len(x)),
    }


def build_latex_unit_root_table(df: pd.DataFrame) -> str:
    latex = (
        "\\begin{table}[H]\n"
        "\\centering\n"
        "\\caption{Unit-root (ADF) and stationarity (KPSS) tests for gold and silver, 2006--2024}\n"
        "\\label{tab:unit-root-tests}\n"
        "\\begin{tabular}{llcccc}\n"
        "\\toprule\n"
        "Series & Deterministic & ADF & $p$-value & KPSS & $p$-value \\\\\n"
        "\\midrule\n"
    )
    for _, row in df.iterrows():
        kpss_p = f"{row['kpss_pvalue']:.3f}"
        if row["kpss_pvalue_bound"]:
            kpss_p = f"${row['kpss_pvalue_bound']}{row['kpss_pvalue']:.2f}$"
        latex += (
            f"{row['series']} & {row['deterministic']} & {row['adf_stat']:.3f} & "
            f"{row['adf_pvalue']:.3f} & {row['kpss_stat']:.3f} & {kpss_p} \\\\\n"
        )
    latex += (
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\vspace{0.2cm}\n"
        "\\begin{minipage}{0.9\\textwidth}\n"
        "\\footnotesize\n"
        "\\textit{Notes}: Augmented Dickey--Fuller test (null: unit root; lag length chosen by AIC) and "
        "KPSS test (null: level or trend stationarity; automatic bandwidth) computed with statsmodels. "
        "Log prices are tested with a constant and with a constant plus linear trend; daily log returns "
        "with a constant. KPSS $p$-values are interpolated from tabulated critical values and are bounded "
        "between 0.01 and 0.10.\n"
        "\\end{minipage}\n"
        "\\end{table}\n"
    )
    return latex


def main():
    levels = pd.read_csv(DATA_PROCESSED_DIR / "asset_levels.csv", index_col=0, parse_dates=True)
    returns = pd.read_csv(DATA_PROCESSED_DIR / "asset_returns.csv", index_col=0, parse_dates=True)

    log_gold = np.log(levels["gold"])
    log_silver = np.log(levels["silver"])
    gold_ret = returns["gold"]
    silver_ret = returns["silver"]

    gold_price_res = ar1_results(log_gold)
    silver_price_res = ar1_results(log_silver)
    gold_ret_res = ar1_results(gold_ret)
    silver_ret_res = ar1_results(silver_ret)

    ar_price = pd.DataFrame(
        {
            "phi": [gold_price_res[0], silver_price_res[0]],
            "se_phi": [gold_price_res[1], silver_price_res[1]],
            "t_phi": [gold_price_res[2], silver_price_res[2]],
            "R2": [gold_price_res[3], silver_price_res[3]],
        },
        index=["Gold (log price)", "Silver (log price)"],
    )

    ar_return = pd.DataFrame(
        {
            "phi": [gold_ret_res[0], silver_ret_res[0]],
            "se_phi": [gold_ret_res[1], silver_ret_res[1]],
            "t_phi": [gold_ret_res[2], silver_ret_res[2]],
            "R2": [gold_ret_res[3], silver_ret_res[3]],
        },
        index=["Gold (return)", "Silver (return)"],
    )

    print("AR(1) on log prices:")
    print(ar_price)

    print("\nAR(1) on log returns:")
    print(ar_return)

    stylized = pd.DataFrame(
        {
            "mean": returns[["gold", "silver"]].mean(),
            "std": returns[["gold", "silver"]].std(),
            "skewness": returns[["gold", "silver"]].apply(skew),
            "excess_kurtosis": returns[["gold", "silver"]].apply(lambda x: kurtosis(x, fisher=True)),
            "acf_abs_ret_1": returns[["gold", "silver"]].apply(lambda x: acf(np.abs(x), nlags=5, fft=False)[1]),
            "acf_sq_ret_1": returns[["gold", "silver"]].apply(lambda x: acf((x ** 2), nlags=5, fft=False)[1]),
        }
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_csv(stylized, "stylized_facts_summary.csv")
    save_csv(ar_price, "ar1_log_prices.csv")
    save_csv(ar_return, "ar1_returns.csv")

    unit_root = pd.DataFrame(
        [
            unit_root_row(log_gold, "Gold log price", "c"),
            unit_root_row(log_gold, "Gold log price", "ct"),
            unit_root_row(log_silver, "Silver log price", "c"),
            unit_root_row(log_silver, "Silver log price", "ct"),
            unit_root_row(gold_ret, "Gold return", "c"),
            unit_root_row(silver_ret, "Silver return", "c"),
        ]
    )
    print("\nADF / KPSS tests:")
    print(unit_root)
    save_csv(unit_root, "unit_root_tests.csv", index=False)
    write_text_file(build_latex_unit_root_table(unit_root), "unit_root_tests.tex", subdir="tables")


if __name__ == "__main__":
    main()