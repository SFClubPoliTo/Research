import pandas as pd
from statsmodels.stats.multitest import multipletests

from config import DATA_PROCESSED_DIR, OUTPUT_DIR
from utils import newey_west_maxlags, run_ols_formula, save_csv, write_text_file

DISPLAY_NAMES = {
    "Intercept": "Constant",
    "ust10y_change": r"$\Delta y^{10Y}_t$",
    "sp500": r"$r^{equity}_t$",
    "dxy": r"$r^{usd}_t$",
}

REGRESSOR_ORDER = ["dxy", "ust10y_change", "sp500", "Intercept"]


def significance_stars(pval: float) -> str:
    if pval < 0.01:
        return "***"
    if pval < 0.05:
        return "**"
    if pval < 0.10:
        return "*"
    return ""


def format_coef(model, var_name: str) -> str:
    if var_name not in model.params.index:
        return ""
    coef = model.params[var_name]
    pval = model.pvalues[var_name]
    return f"{coef:.4f}{significance_stars(pval)}"


def format_se(model, var_name: str) -> str:
    if var_name not in model.bse.index:
        return ""
    se = model.bse[var_name]
    return f"({se:.4f})"


def build_regression_table(models, model_labels):
    rows = []

    for var in REGRESSOR_ORDER:
        label = DISPLAY_NAMES[var]
        coef_row = [label]
        se_row = [""]

        for model in models:
            # The formula API names the constant "Intercept"; sm.add_constant names it "const".
            statsmodels_name = var
            if var == "Intercept" and "Intercept" not in model.params.index:
                statsmodels_name = "const"
            coef_row.append(format_coef(model, statsmodels_name))
            se_row.append(format_se(model, statsmodels_name))

        rows.append(coef_row)
        rows.append(se_row)

    rows.append(["Observations"] + [f"{int(model.nobs)}" for model in models])
    rows.append([r"$R^2$"] + [f"{model.rsquared:.3f}" for model in models])
    rows.append(["Adjusted $R^2$"] + [f"{model.rsquared_adj:.3f}" for model in models])

    table = pd.DataFrame(rows, columns=[""] + model_labels)
    return table


def model_key(model):
    dependent = model.model.endog_names
    regressors = " + ".join(sorted(name for name in model.params.index if name != "Intercept"))
    return dependent, regressors


def holm_adjusted_pvalues(model_groups) -> pd.DataFrame:
    """
    Holm (1979) step-down adjustment over all distinct slope-coefficient tests
    reported in the six regression tables. Specification (2) appears in three
    tables per asset, so duplicated regressions are counted once.
    """
    rows = []
    seen = set()
    for models in model_groups:
        for model in models:
            key = model_key(model)
            if key in seen:
                continue
            seen.add(key)
            for var in model.params.index:
                if var == "Intercept":
                    continue
                rows.append(
                    {
                        "dependent": key[0],
                        "regressors": key[1],
                        "variable": var,
                        "coef": model.params[var],
                        "se_hac": model.bse[var],
                        "pvalue": model.pvalues[var],
                    }
                )

    holm = pd.DataFrame(rows)
    holm["pvalue_holm"] = multipletests(holm["pvalue"], method="holm")[1]
    return holm


def holm_note(models, holm: pd.DataFrame) -> str:
    lost = []
    for model in models:
        dependent, regressors = model_key(model)
        sub = holm[(holm["dependent"] == dependent) & (holm["regressors"] == regressors)]
        for _, row in sub.iterrows():
            if row["pvalue"] < 0.05 <= row["pvalue_holm"]:
                lost.append(DISPLAY_NAMES[row["variable"]])

    if lost:
        detail = (
            "the following coefficients are no longer significant at the 5\\% level: "
            + ", ".join(sorted(set(lost)))
            + "."
        )
    else:
        detail = "every slope coefficient significant at the 5\\% level in this table remains so."

    return (
        "Stars refer to unadjusted $p$-values. After a Holm adjustment across the "
        f"{len(holm)} distinct slope tests reported in the six regression tables, {detail}"
    )


def export_table_latex(table, filename, caption, label, nobs, extra_note=""):
    latex_str = table.to_latex(
        index=False,
        escape=False,
        column_format="l" + "c" * (table.shape[1] - 1)
    )

    wrapped = (
        "\\begin{table}[H]\n"
        "\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        f"{latex_str}\n"
        "\\vspace{0.2cm}\n"
        "\\begin{minipage}{0.9\\textwidth}\n"
        "\\footnotesize\n"
        "\\textit{Notes}: Daily data. Newey--West heteroskedasticity- and autocorrelation-consistent (HAC) "
        f"standard errors in parentheses (Bartlett kernel, {newey_west_maxlags(nobs)} lags).\\\\\n"
        "$^*$ $p<0.10$, $^{**}$ $p<0.05$, $^{***}$ $p<0.01$. "
        f"{extra_note}\n"
        "\\end{minipage}\n"
        "\\end{table}\n"
    )

    write_text_file(wrapped, filename, subdir="tables")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    returns = pd.read_csv(DATA_PROCESSED_DIR / "asset_returns.csv", index_col=0, parse_dates=True)
    data = returns.dropna().copy()

    gold_bond_models = [
        run_ols_formula("gold ~ ust10y_change", data),
        run_ols_formula("gold ~ ust10y_change + sp500 + dxy", data),
    ]
    gold_equity_models = [
        run_ols_formula("gold ~ sp500", data),
        run_ols_formula("gold ~ sp500 + ust10y_change + dxy", data),
    ]
    gold_dollar_models = [
        run_ols_formula("gold ~ dxy", data),
        run_ols_formula("gold ~ dxy + ust10y_change + sp500", data),
    ]

    silver_bond_models = [
        run_ols_formula("silver ~ ust10y_change", data),
        run_ols_formula("silver ~ ust10y_change + sp500 + dxy", data),
    ]
    silver_equity_models = [
        run_ols_formula("silver ~ sp500", data),
        run_ols_formula("silver ~ sp500 + ust10y_change + dxy", data),
    ]
    silver_dollar_models = [
        run_ols_formula("silver ~ dxy", data),
        run_ols_formula("silver ~ dxy + ust10y_change + sp500", data),
    ]

    gold_bond_table = build_regression_table(gold_bond_models, ["(1)", "(2)"])
    gold_equity_table = build_regression_table(gold_equity_models, ["(1)", "(2)"])
    gold_dollar_table = build_regression_table(gold_dollar_models, ["(1)", "(2)"])

    silver_bond_table = build_regression_table(silver_bond_models, ["(1)", "(2)"])
    silver_equity_table = build_regression_table(silver_equity_models, ["(1)", "(2)"])
    silver_dollar_table = build_regression_table(silver_dollar_models, ["(1)", "(2)"])

    holm = holm_adjusted_pvalues(
        [
            gold_bond_models, gold_equity_models, gold_dollar_models,
            silver_bond_models, silver_equity_models, silver_dollar_models,
        ]
    )
    save_csv(holm, "regression_holm_adjusted_pvalues.csv", index=False)

    save_csv(gold_bond_table, "gold_bond_regressions.csv", index=False)
    save_csv(gold_equity_table, "gold_equity_regressions.csv", index=False)
    save_csv(gold_dollar_table, "gold_dollar_regressions.csv", index=False)
    save_csv(silver_bond_table, "silver_bond_regressions.csv", index=False)
    save_csv(silver_equity_table, "silver_equity_regressions.csv", index=False)
    save_csv(silver_dollar_table, "silver_dollar_regressions.csv", index=False)

    export_table_latex(
        gold_bond_table,
        "gold_bond_regressions.tex",
        "OLS regressions of daily gold returns on bond, dollar, and equity variables",
        "tab:ols_gold_bond",
        nobs=int(gold_bond_models[0].nobs),
        extra_note=holm_note(gold_bond_models, holm),
    )
    export_table_latex(
        gold_equity_table,
        "gold_equity_regressions.tex",
        "OLS regressions of daily gold returns on equity, bond, and dollar variables",
        "tab:ols_gold_equity",
        nobs=int(gold_equity_models[0].nobs),
        extra_note=holm_note(gold_equity_models, holm),
    )
    export_table_latex(
        gold_dollar_table,
        "gold_dollar_regressions.tex",
        "OLS regressions of daily gold returns on dollar, bond, and equity variables",
        "tab:ols_gold_dollar",
        nobs=int(gold_dollar_models[0].nobs),
        extra_note=holm_note(gold_dollar_models, holm),
    )
    export_table_latex(
        silver_bond_table,
        "silver_bond_regressions.tex",
        "OLS regressions of daily silver returns on bond, dollar, and equity variables",
        "tab:ols_silver_bond",
        nobs=int(silver_bond_models[0].nobs),
        extra_note=holm_note(silver_bond_models, holm),
    )
    export_table_latex(
        silver_equity_table,
        "silver_equity_regressions.tex",
        "OLS regressions of daily silver returns on equity, bond, and dollar variables",
        "tab:ols_silver_equity",
        nobs=int(silver_equity_models[0].nobs),
        extra_note=holm_note(silver_equity_models, holm),
    )
    export_table_latex(
        silver_dollar_table,
        "silver_dollar_regressions.tex",
        "OLS regressions of daily silver returns on dollar, bond, and equity variables",
        "tab:ols_silver_dollar",
        nobs=int(silver_dollar_models[0].nobs),
        extra_note=holm_note(silver_dollar_models, holm),
    )


if __name__ == "__main__":
    main()
