"""Rebuild the Paper evidence on the dated clock with the GLD carry.

Stages (run in order; each reads the previous stage's files):

  calibration  audit the q = 0.40% CC64 fit of 2 September 2026: nested
               refinements (Heston within Bates within Bates-Hawkes), Feller
               and identification diagnostics, residuals, audited parameters;
  valuation    four-engine operating proxy on the dated clock
               (``barrick_unified.dated_valuation``) with the corrected path
               engines, terminal policies, risk-free comparison, numerical
               sensitivity, path validation against COS and the attribution
               of each correction relative to the 7 September Paper;
  oos          rolling OOS audit of the carry-consistent run, with
               Diebold-Mariano tests (Newey-West variance) against both
               benchmarks and between models.

The historical 7 September chain (``paper_cli.py``) is untouched and still
replays its own outputs.  Nothing here is a fair value or target price.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.optimize import brentq, minimize
from scipy.special import ndtr
from scipy.stats import norm
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
sys.path[:0] = [str(R / "src/pricing"), str(R / "src")]
from Heston import Heston  # noqa: E402
from Bates import Bates  # noqa: E402
from BatesHawkesExact import BatesHawkesExact  # noqa: E402
from Hawkes import ExactHawkesCalibration as Hawkes  # noqa: E402
from barrick_unified.multimodel_valuation import MODEL_ORDER, load_multimodel_inputs  # noqa: E402
from barrick_unified.dated_valuation import build_schedule, daily_forward_rates, value_dated, DAYS_PER_YEAR  # noqa: E402
from barrick_unified.gold_paths import simulate_model, validate_against_cos  # noqa: E402

LABELS = {"black_scholes": "Black-Scholes", "heston": "Heston", "bates_poisson": "Bates-Poisson",
          "full_bates_hawkes": "Bates-Hawkes"}
FILES = {"black_scholes": "black_scholes", "heston": "heston", "bates_poisson": "bates",
         "full_bates_hawkes": "full_bates_hawkes"}
HAWKES_NAMES = ["v0", "kappa", "theta", "xi", "rho", "lambda0", "lambda_bar", "branching_ratio", "beta", "mu_J", "sigma_J"]
HAWKES_BOUNDS = [(1e-4, 1), (.1, 10), (1e-4, 1), (.01, 8), (-.99, .99), (1e-6, 5), (1e-6, 5), (0, .95), (.1, 12),
                 (-.5, .5), (1e-4, .6)]
COLORS = ["#7287b1", "#d59655", "#55968b", "#825da9"]
GLD_FEE = 0.004
FELLER = ({"type": "ineq", "fun": lambda x: 2 * x[1] * x[2] - x[3] ** 2},)


def save_figure(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=240)
    plt.close(fig)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=float), encoding="utf-8")


def bs_call(S, K, T, r, v):
    d1 = (np.log(S / K) + (r + .5 * v * v) * T) / (v * np.sqrt(T))
    return S * ndtr(d1) - K * np.exp(-r * T) * ndtr(d1 - v * np.sqrt(T))


def model_prices(model: str, p: dict, f: pd.DataFrame, spot: float) -> np.ndarray:
    prices = np.zeros(len(f))
    for (T, r), g in f.groupby(["T", "rate"]):
        K = g.K.to_numpy()
        if model == "black_scholes":
            v = bs_call(spot, K, T, r, p["sigma"])
        elif model == "heston":
            v = Heston.heston_prices_cos(spot, K, T, *[p[n] for n in Heston.PARAMETER_NAMES], r, N=256)
        elif model == "bates_poisson":
            v = Bates.bates_prices_cos(spot, K, T, *[p[n] for n in Bates.PARAMETER_NAMES], r, N=256)
        else:
            v = BatesHawkesExact.hawkes_price_cos(spot, K, T, *[p[n] for n in ["v0", "kappa", "theta", "xi", "rho",
                                                   "lambda0", "lambda_bar", "alpha", "beta", "mu_J", "sigma_J"]], r, N=256)
        prices[g.index] = v
    return prices


def stage_calibration(a) -> None:
    D, A, O, F = Path(a.calibration_dir), Path(a.audited_dir), Path(a.output_dir), Path(a.figure_dir)
    f = pd.read_csv(D / "calibration_surface.csv")
    q = float(f["dividend_yield_applied"].iloc[0])
    spot = float(f.spot.iloc[0])
    raw = {m: json.loads((D / f"{FILES[m]}.json").read_text()) for m in MODEL_ORDER}
    heston = np.array([raw["heston"]["parameters"][n] for n in Heston.PARAMETER_NAMES])
    loss_h = Heston.heston_objective(heston, f, spot, cos_N=256)

    # Bates: the nested Heston point (lambda = 0) is always a candidate.
    nested = np.r_[heston, 0.0, 0.0, 0.1]
    original = np.array([raw["bates_poisson"]["parameters"][n] for n in Bates.PARAMETER_NAMES])
    candidates = [nested, original]
    for start in (nested, original):
        z = minimize(Bates.bates_objective, start, args=(f, spot, 0., "cos", 256), method="SLSQP",
                     bounds=Bates.BOUNDS, constraints=FELLER, options={"ftol": 1e-12, "maxiter": 150})
        candidates.append(z.x)
    bates = min(candidates, key=lambda x: Bates.bates_objective(x, f, spot, cos_N=256))
    loss_b = Bates.bates_objective(bates, f, spot, cos_N=256)
    assert loss_b <= loss_h + 1e-12

    # Bates-Hawkes: nested Bates point (branching 0, constant intensity) kept.
    nested_h = np.r_[bates[:5], bates[5], bates[5], 0.0, 2.0, bates[6:]]
    hp = raw["full_bates_hawkes"]["parameters"]
    original_h = np.array([hp[n] for n in HAWKES_NAMES])
    candidates = [nested_h, original_h]
    for start in (nested_h, original_h):
        z = minimize(Hawkes.objective_heston, start, args=(f, spot, 0., None, 256), method="SLSQP",
                     bounds=HAWKES_BOUNDS, constraints=FELLER, options={"ftol": 1e-11, "maxiter": 100})
        candidates.append(z.x)
    hawkes = min(candidates, key=lambda x: Hawkes.objective_heston(x, f, spot, cos_N=256))
    loss_hk = Hawkes.objective_heston(hawkes, f, spot, cos_N=256)
    assert loss_hk <= loss_b + 1e-10

    params = {
        "black_scholes": dict(raw["black_scholes"]["parameters"]),
        "heston": dict(zip(Heston.PARAMETER_NAMES, heston)),
        "bates_poisson": dict(zip(Bates.PARAMETER_NAMES, bates)),
        "full_bates_hawkes": Hawkes.unpack_heston_params(hawkes),
    }
    losses = {"black_scholes": raw["black_scholes"]["objective"], "heston": loss_h, "bates_poisson": loss_b,
              "full_bates_hawkes": loss_hk}

    # Feller gap at the optimum, and a Feller-relaxed Heston fit.
    def feller(p, vol="sigma"):
        gap = 2 * p["kappa"] * p["theta"] - p[vol] ** 2
        return {"two_kappa_theta": 2 * p["kappa"] * p["theta"], "vol_of_vol_squared": p[vol] ** 2,
                "gap": gap, "active": bool(abs(gap) < 1e-3 * p[vol] ** 2)}

    def heston_free(x):
        if not (x[0] > 0 and x[1] > 0 and x[2] > 0 and x[3] > 0 and -1 < x[4] < 1):
            return 1e8
        err = 0.0
        for (T, r), g in f.groupby(["T", "rate"]):
            v = Heston.heston_prices_cos(spot, g.K.to_numpy(), T, *x, r, N=256)
            err += float(np.sum(((v - g.price.to_numpy()) / np.maximum(g.vega.to_numpy(), 1e-4)) ** 2))
        return err / len(f)

    relaxed = minimize(heston_free, heston, method="L-BFGS-B", bounds=Heston.BOUNDS, options={"maxiter": 400})
    # Profile of the Heston loss in kappa: other parameters re-optimised.
    profile = []
    for kappa in (0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0):
        start = heston.copy()
        start[1] = kappa
        start[3] = min(start[3], 0.99 * np.sqrt(2 * kappa * start[2]))
        z = minimize(lambda x: Heston.heston_objective(np.r_[x[0], kappa, x[1:]], f, spot, cos_N=256),
                     np.r_[start[0], start[2:]], method="SLSQP",
                     bounds=[Heston.BOUNDS[0]] + list(Heston.BOUNDS[2:]),
                     constraints=({"type": "ineq", "fun": lambda x: 2 * kappa * x[1] - x[2] ** 2},),
                     options={"ftol": 1e-12, "maxiter": 200})
        profile.append({"kappa": kappa, "loss": float(z.fun), "loss_ratio_to_optimum": float(z.fun / loss_h)})
    pd.DataFrame(profile).to_csv(O / "heston_kappa_profile.csv", index=False)

    summary, residuals = [], {}
    for m in MODEL_ORDER:
        prices = model_prices(m, params[m], f, spot)
        iv = np.array([brentq(lambda s: bs_call(spot, row.K, row.T, row.rate, s) - price, 1e-7, 5)
                       for row, price in zip(f.itertuples(), prices)])
        res = (f.implied_vol.to_numpy() - iv) * 1e4
        residuals[m] = res
        summary.append({"model": m, "label": LABELS[m], "vega_scaled_mse": losses[m],
                        "iv_rmse_bp": float(np.sqrt(np.mean(res ** 2))), "dividend_yield": q})
        pd.DataFrame({"K": f.K, "K_quoted": f.K_quoted, "T": f["T"], "market_iv": f.implied_vol, "model_iv": iv,
                      "residual_bp": res}).to_csv(O / f"{m}_residuals.csv", index=False)
    pd.DataFrame(summary).to_csv(O / "calibration_summary_audited.csv", index=False)
    limit = max(np.abs(r).max() for r in residuals.values())
    for m in MODEL_ORDER:
        fig, ax = plt.subplots(figsize=(6, 2.7))
        im = ax.scatter(f.K_quoted / spot, f["T"], c=residuals[m], cmap="coolwarm", vmin=-limit, vmax=limit, s=33,
                        marker="s")
        fig.colorbar(im, ax=ax, label="Market IV - model IV (bp)")
        ax.set(xlabel="Strike / spot", ylabel="Maturity (years)", title=f"{LABELS[m]} | q = 0.40% | common scale")
        save_figure(fig, F / f"{FILES[m] if m != 'full_bates_hawkes' else 'bates_hawkes'}_residual_heatmap.png")

    A.mkdir(parents=True, exist_ok=True)
    for m in MODEL_ORDER:
        payload = dict(raw[m])
        payload.update(parameters={k: float(v) for k, v in params[m].items()}, objective=float(losses[m]),
                       audit_date="2026-10-24", dividend_yield=q,
                       source_calibration=str((D / f"{FILES[m]}.json").relative_to(R)).replace("\\", "/"))
        write_json(A / f"{FILES[m]}.json", payload)
    write_json(A / "manifest.json", {
        "date": "2026-09-02", "strategy": "CC", "n_calibration": int(len(f)), "spot": spot, "dividend_yield": q,
        "source_dir": str(D.relative_to(R)).replace("\\", "/"), "audit_date": "2026-10-24",
        "nesting": "Heston within Bates within Bates-Hawkes; nested candidates always retained"})
    write_json(O / "calibration_audit.json", {
        "dividend_yield": q, "losses": losses,
        "nesting_holds": bool(loss_hk <= loss_b + 1e-10 and loss_b <= loss_h + 1e-12),
        "feller": {"heston": feller(params["heston"]), "bates_poisson": feller(params["bates_poisson"]),
                   "full_bates_hawkes": feller(params["full_bates_hawkes"], "xi")},
        "feller_relaxed_heston": {"loss": float(relaxed.fun), "parameters": dict(zip(Heston.PARAMETER_NAMES,
                                  map(float, relaxed.x))), "loss_ratio_to_constrained": float(relaxed.fun / loss_h)},
        "bates_jump_intensity": float(params["bates_poisson"]["lambd"]),
        "kappa_profile_max_loss_ratio": float(max(r["loss_ratio_to_optimum"] for r in profile)),
        "interpretation": "Feller enforced as a hard constraint; kappa and jump parameters are weakly identified "
                          "on 64 calls (see heston_kappa_profile.csv)."})
    print(pd.DataFrame(summary).to_string(index=False))


def _inputs(cfg):
    inputs, _ = load_multimodel_inputs(R, cfg)
    start = cfg["gold_price_layer"]["common_scenario_start"]["price"]
    return replace(inputs, gold_price_0_usd_per_oz=float(start))


def run_engines(cfg, parameter_dir: Path, n_paths: int, seed_offset: int = 0, start: float | None = None):
    base = json.loads((R / cfg["base_valuation_config"]).read_text(encoding="utf-8"))
    clock = cfg["valuation_clock"]
    inputs = _inputs(cfg)
    if start is not None:
        inputs = replace(inputs, gold_price_0_usd_per_oz=float(start))
    schedule = build_schedule(clock["valuation_date"], clock["horizon_end"], clock["first_operating_quarter"],
                              base["model"]["operating_vector_status"])
    rates = daily_forward_rates(inputs.nss_parameters, schedule.horizon_days)
    seed = int(cfg["simulation"]["engine_seed"]) + seed_offset
    shocks = np.random.default_rng(int(cfg["simulation"]["wacc_seed"]) + seed_offset).standard_normal(
        (n_paths, schedule.rate_years - 1))
    out = {}
    for m in MODEL_ORDER:
        p = json.loads((parameter_dir / f"{FILES[m]}.json").read_text())["parameters"]
        paths = simulate_model(m, p, inputs.gold_price_0_usd_per_oz, rates, 1.0 / DAYS_PER_YEAR, n_paths, seed)
        out[m] = {policy: value_dated(inputs, schedule, paths, shocks, inputs.nss_parameters, policy)
                  for policy in ("signed", "none", "legacy_positive")}
        del paths
    return inputs, schedule, out


def stage_valuation(a) -> None:
    O, F = Path(a.output_dir), Path(a.figure_dir)
    cfg = json.loads((R / a.config).read_text(encoding="utf-8"))
    n = int(cfg["simulation"]["n_simulations"])
    A = R / cfg["gold_price_layer"]["parameter_dir"]
    inputs, schedule, runs = run_engines(cfg, A, n)
    base = json.loads((R / cfg["base_valuation_config"]).read_text(encoding="utf-8"))["model"]
    pd.DataFrame([{"quarter": q.quarter, "remaining_days": q.days_remaining,
                   "remaining_fraction": q.calendar_fraction_remaining, "flow_years": t,
                   "production_koz": inputs.production_koz[i], "unit_cost_usd_per_oz": inputs.cost_usd_per_oz[i],
                   "operating_status": base["operating_vector_status"][i]}
                  for q, t, i in zip(schedule.quarters, schedule.flow_years, schedule.operating_index)]
                 ).to_csv(O / "dated_schedule.csv", index=False)
    rows, policies, samples = [], [], {}
    for m, v in runs.items():
        x = v["signed"].enterprise_value_proxy_usd_mn / 1000
        samples[m] = x
        rows.append({"model": m, "p10_bn": np.quantile(x, .1), "median_bn": np.median(x), "p90_bn": np.quantile(x, .9),
                     "mean_bn": x.mean(), "mc_mean_se_bn": x.std(ddof=1) / np.sqrt(len(x)),
                     "negative_fraction": np.mean(x < 0),
                     "five_year_median_bn": np.median(v["none"].enterprise_value_proxy_usd_mn) / 1000,
                     "terminal_share_of_mean": float(v["signed"].pv_terminal_usd_mn.mean()
                                                     / v["signed"].enterprise_value_proxy_usd_mn.mean()),
                     "explicit_wacc_median_bn": np.median(v["signed"].pv_explicit_usd_mn) / 1000,
                     "explicit_risk_free_median_bn": np.median(v["signed"].pv_explicit_risk_free_usd_mn) / 1000})
        for label, policy in (("Signed perpetuity", "signed"), ("Explicit flows only", "none"),
                              ("Positive-floor perpetuity", "legacy_positive")):
            policies.append({"model": m, "policy": label,
                             "median_bn": np.median(v[policy].enterprise_value_proxy_usd_mn) / 1000})
        policies.append({"model": m, "policy": "Explicit flows, risk-free discounting",
                         "median_bn": np.median(v["signed"].pv_explicit_risk_free_usd_mn) / 1000})
    summary = pd.DataFrame(rows)
    summary.to_csv(O / "proxy_summary.csv", index=False)
    pd.DataFrame(policies).to_csv(O / "terminal_policy_comparison.csv", index=False)
    np.savez_compressed(O / "proxy_samples.npz", **samples)
    print(summary.to_string(index=False))

    sens = []
    for count, offset in ((n, 0), (2 * n, 0), (n, 1), (n, 2)):
        _, _, extra = (inputs, schedule, runs) if (count, offset) == (n, 0) else run_engines(cfg, A, count, offset)
        for m, v in extra.items():
            x = v["signed"].enterprise_value_proxy_usd_mn / 1000
            sens.append({"model": m, "paths": count, "seed_offset": offset, "mean_bn": x.mean(),
                         "mc_mean_se_bn": x.std(ddof=1) / np.sqrt(len(x)), "median_bn": np.median(x),
                         "p90_bn": np.quantile(x, .9)})
    sens = pd.DataFrame(sens)
    sens.to_csv(O / "numerical_sensitivity.csv", index=False)

    # Attribution: the 7 September Paper, then each correction in turn.
    legacy = pd.read_csv(R / "outputs/paper_audit/proxy_summary.csv").set_index("model")["median_bn"]
    old_params = R / "data/processed/team8/calibration_audited_20260907"
    steps = [("7 Sep Paper (legacy clock, frozen engines)", None)]
    _, _, timing = run_engines(cfg, old_params, n, start=4417.0)
    _, _, anchor = run_engines(cfg, old_params, n)
    attribution = []
    for m in MODEL_ORDER:
        attribution += [
            {"model": m, "step": steps[0][0], "median_bn": float(legacy[m])},
            {"model": m, "step": "+ dated clock, path average, mid-period, corrected engines",
             "median_bn": np.median(timing[m]["signed"].enterprise_value_proxy_usd_mn) / 1000},
            {"model": m, "step": "+ spot anchor USD 4,391.32/oz at valuation time",
             "median_bn": np.median(anchor[m]["signed"].enterprise_value_proxy_usd_mn) / 1000},
            {"model": m, "step": "+ GLD carry q = 0.40% recalibration (final)", "median_bn": float(np.median(samples[m]))},
        ]
    pd.DataFrame(attribution).to_csv(O / "correction_attribution.csv", index=False)

    stage_path_validation(a)

    labels = [LABELS[m] for m in MODEL_ORDER]
    fig, ax = plt.subplots(figsize=(6, 3))
    x = samples["full_bates_hawkes"]
    ax.hist(x, bins=85, color=COLORS[-1], alpha=.65, density=True)
    ax.axvline(0, color="black", lw=.7)
    ax.set(xlabel="Operating proxy (USD billion)", ylabel="Density", title="Bates-Hawkes | dated clock | signed terminal")
    ax.set_xlim(np.quantile(x, .005), np.quantile(x, .995))
    save_figure(fig, F / "fig_val_primary.png")
    fig, ax = plt.subplots(figsize=(6, 3))
    for m, label, col in zip(MODEL_ORDER, labels, COLORS):
        ax.hist(samples[m], bins=np.linspace(-80, 300, 100), histtype="step", density=True, label=label, color=col)
    ax.set(xlabel="Operating proxy (USD billion)", ylabel="Density", title="Common operating inputs | no equity bridge")
    ax.legend(fontsize=7)
    save_figure(fig, F / "fig_val_multi.png")
    fig, ax = plt.subplots(figsize=(6.4, 3))
    pol = pd.DataFrame(policies)
    order = ["Explicit flows, risk-free discounting", "Explicit flows only", "Signed perpetuity", "Positive-floor perpetuity"]
    xx = np.arange(4)
    for i, policy in enumerate(order):
        ax.bar(xx + (i - 1.5) * .2, pol[pol.policy == policy].median_bn, width=.2, label=policy)
    ax.set_xticks(xx, labels, rotation=10)
    ax.set(ylabel="Median proxy (USD billion)", title="Terminal closure and discounting are assumptions")
    ax.legend(fontsize=6.5)
    save_figure(fig, F / "fig_terminal_share.png")
    att = pd.DataFrame(attribution)
    fig, ax = plt.subplots(figsize=(6.4, 3))
    for m, label, col in zip(MODEL_ORDER, labels, COLORS):
        ax.plot(range(4), att[att.model == m].median_bn, marker="o", color=col, label=label)
    ax.set_xticks(range(4), ["7 Sep Paper", "+ dated clock", "+ spot anchor", "+ GLD carry"], fontsize=7)
    ax.set(ylabel="Median proxy (USD billion)", title="Effect of each correction on the median proxy")
    ax.legend(fontsize=7)
    save_figure(fig, F / "fig_correction_attribution.png")


def stage_path_validation(a) -> None:
    cfg = json.loads((R / a.config).read_text(encoding="utf-8"))
    A = R / cfg["gold_price_layer"]["parameter_dir"]
    params = {m: json.loads((A / f"{FILES[m]}.json").read_text())["parameters"] for m in MODEL_ORDER}
    table = pd.DataFrame(validate_against_cos(params, maturities=(1.0, 3.0)))
    table.to_csv(Path(a.output_dir) / "path_validation_cos.csv", index=False)
    print(table.round(4).to_string(index=False))


COPPER_MODELS = {"black_scholes": "Black-76", "heston": "Heston-forward", "bates_poisson": "Bates-Poisson-forward",
                 "full_bates_hawkes": "Full-Bates-Hawkes-forward"}


def stage_copper(a) -> None:
    """Paired gold-only vs gold+copper proxies on the dated clock."""
    from barrick_unified.copper import attributable_copper_margin
    from run_copper_valuation import couple_by_terminal_scores

    O = Path(a.output_dir)
    cfg = json.loads((R / a.config).read_text(encoding="utf-8"))
    n = int(cfg["simulation"]["n_simulations"])
    A = R / cfg["gold_price_layer"]["parameter_dir"]
    C = R / "data/processed/copper/snapshot_20260902"
    copper = json.loads((C / "copper_parameters.json").read_text())
    anchors = pd.read_csv(C / "copper_forward_delivery_anchors.csv").set_index("future_delivery_years").forward_usd_per_lb
    ops = json.loads((R / "data/processed/config/copper_operating_20260902.json").read_text())
    base = json.loads((R / cfg["base_valuation_config"]).read_text(encoding="utf-8"))
    clock = cfg["valuation_clock"]
    inputs = _inputs(cfg)
    schedule = build_schedule(clock["valuation_date"], clock["horizon_end"], clock["first_operating_quarter"],
                              base["model"]["operating_vector_status"])
    rates = daily_forward_rates(inputs.nss_parameters, schedule.horizon_days)
    times = np.arange(schedule.horizon_days + 1) / DAYS_PER_YEAR
    # Log-linear matched-future anchors, flat beyond the last observed delivery:
    # a cross-delivery scenario mean, not the drift of one fixed future.
    start = float(anchors.iloc[0])
    targets = np.exp(np.interp(times, np.r_[0.0, anchors.index], np.log(np.r_[start, anchors.to_numpy()])))
    copper_drift = np.diff(np.log(targets)) * DAYS_PER_YEAR
    sales = np.array([m["sales_kt"] for m in ops["mines"]], dtype=float)[:, None].repeat(len(schedule.quarters), 1)
    costs = np.array([m["cost_of_sales_usd_per_lb"] for m in ops["mines"]], dtype=float)[:, None].repeat(len(schedule.quarters), 1)
    shocks = np.random.default_rng(int(cfg["simulation"]["wacc_seed"])).standard_normal((n, schedule.rate_years - 1))
    rows = []
    for m in MODEL_ORDER:
        p = json.loads((A / f"{FILES[m]}.json").read_text())["parameters"]
        gold = simulate_model(m, p, inputs.gold_price_0_usd_per_oz, rates, 1 / DAYS_PER_YEAR, n,
                              int(cfg["simulation"]["engine_seed"]))
        cu = simulate_model(m, copper[COPPER_MODELS[m]]["parameters"], start, copper_drift, 1 / DAYS_PER_YEAR, n, 20262003)
        cu_q = np.column_stack([cu[:, x:y].mean(axis=1) for x, y in zip(schedule.start_day, schedule.end_day)])
        for rho in (0.0, -0.5, 0.5):
            coupled = couple_by_terminal_scores(gold[:, schedule.end_day - 1], cu_q, rho, 20263003)
            margin, _ = attributable_copper_margin(coupled, sales, costs)
            for policy, scope in (("none", "explicit_flows_primary"), ("signed", "signed_perpetuity_sensitivity")):
                g = value_dated(inputs, schedule, gold, shocks, inputs.nss_parameters, policy)
                gc = value_dated(inputs, schedule, gold, shocks, inputs.nss_parameters, policy, margin)
                delta = gc.enterprise_value_proxy_usd_mn - g.enterprise_value_proxy_usd_mn
                rows.append({"model": m, "scope": scope, "terminal_score_rho": rho,
                             "gold_only_mean_bn": g.enterprise_value_proxy_usd_mn.mean() / 1000,
                             "gold_plus_copper_mean_bn": gc.enterprise_value_proxy_usd_mn.mean() / 1000,
                             "copper_increment_mean_bn": delta.mean() / 1000,
                             "copper_increment_se_mn": delta.std(ddof=1) / np.sqrt(n),
                             "gold_plus_copper_median_bn": np.median(gc.enterprise_value_proxy_usd_mn) / 1000})
        del gold, cu
    table = pd.DataFrame(rows)
    table.to_csv(O / "copper_paired_summary.csv", index=False)
    print(table.round(3).to_string(index=False))


def newey_west_dm(d: np.ndarray) -> dict:
    d = np.asarray(d, dtype=float)
    d = d[np.isfinite(d)]
    n = len(d)
    lag = int(np.floor(n ** (1 / 3)))
    u = d - d.mean()
    var = u @ u / n
    for k in range(1, lag + 1):
        var += 2 * (1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n
    stat = d.mean() / np.sqrt(var / n)
    return {"dates": n, "lag": lag, "mean_loss_difference": d.mean(), "dm_stat": stat,
            "p_value_two_sided": 2 * norm.sf(abs(stat))}


def oos_tables(dm: pd.DataFrame, run: str) -> tuple[list[dict], list[dict]]:
    rows, tests = [], []
    for model, g in dm.groupby("model", sort=False):
        for label, mc, bc, nc in [("mean", "mse_iv", "mean_benchmark_mse_iv", "common_n"),
                                  ("persistence", "model_mse_on_persistence_support_iv", "persistence_mse_iv",
                                   "persistence_n")]:
            g2 = g[g[nc] > 0]
            x, b = g2[mc].to_numpy(), g2[bc].to_numpy()
            rows.append({"run": run, "model": model, "benchmark": label, "dates": len(g2),
                         "observations": int(g2[nc].sum()), "mean_daily_rmse_bp": np.sqrt(x).mean() * 1e4,
                         "benchmark_mean_daily_rmse_bp": np.sqrt(b).mean() * 1e4, "r2": 1 - x.sum() / b.sum(),
                         "dates_model_beats_benchmark": int(np.sum(x < b))})
            tests.append({"run": run, "comparison": f"{model} vs {label}", **newey_west_dm(x - b)})
    pivot = dm.pivot(index="target_date", columns="model", values="mse_iv").sort_index()
    for other in [c for c in pivot.columns if c != "hawkes"]:
        tests.append({"run": run, "comparison": f"hawkes vs {other}",
                      **newey_west_dm(pivot["hawkes"].to_numpy() - pivot[other].to_numpy())})
    return rows, tests


def stage_oos(a) -> None:
    O, F = Path(a.output_dir), Path(a.figure_dir)
    new = pd.read_csv(R / a.oos_dir / "rolling" / "date_metrics.csv")
    old = pd.read_csv(R / "data/processed/audit_inputs/outputs/oos/rolling/date_metrics.csv")
    rows, tests = oos_tables(new, "q040_equal_search_20261024")
    rows_old, tests_old = oos_tables(old, "legacy_q0_hawkes_warm_start_20260902")
    pd.DataFrame(rows + rows_old).to_csv(O / "oos_audit.csv", index=False)
    pd.DataFrame(tests + tests_old).to_csv(O / "oos_dm_tests.csv", index=False)
    o = pd.DataFrame(rows)
    keys = list(dict.fromkeys(o.model))
    names = {"bs": "Black-Scholes", "heston": "Heston", "bates": "Bates-Poisson", "hawkes": "Bates-Hawkes"}
    fig, ax = plt.subplots(figsize=(6, 2.9))
    mean = o[o.benchmark == "mean"]
    ax.bar([names[k] for k in keys], mean.mean_daily_rmse_bp, color=COLORS)
    ax.axhline(o[o.benchmark == "persistence"].benchmark_mean_daily_rmse_bp.iloc[0], color="black", lw=.8, ls="--",
               label="IV-surface persistence")
    ax.set(ylabel="Mean daily IV RMSE (bp)", title="Rolling repricing | 30 origins | q = 0.40%")
    ax.legend(fontsize=7)
    save_figure(fig, F / "oos_rmse.png")
    fig, ax = plt.subplots(figsize=(6, 2.8))
    xx = np.arange(len(keys))
    for i, bench in enumerate(["mean", "persistence"]):
        ax.bar(xx + (i - .5) * .33, 100 * o[o.benchmark == bench].r2, width=.33, label=bench)
    ax.axhline(0, color="black", lw=.6)
    ax.set_xticks(xx, [names[k] for k in keys], rotation=10)
    ax.set(ylabel="Date-equal R-squared (%)", title="Out-of-sample R-squared against both benchmarks")
    ax.legend(fontsize=7)
    save_figure(fig, F / "oos_r2.png")
    print(pd.DataFrame(rows).to_string(index=False))
    print(pd.DataFrame(tests).to_string(index=False))


def stage_carry(a) -> None:
    """How the GLD carry changes the fit; call-only surfaces cannot fix the forward."""
    from BnS import BnS
    from gld_carry import forward_equivalent_surface

    O = Path(a.output_dir)
    raw = pd.read_csv(R / "data/processed/audit_inputs/outputs/sampling/2026-09-02/sample_CC_64.csv")
    spot = float(raw.spot.iloc[0])
    start = np.array([0.0644, 4.05, 0.0655, 0.728, -0.017])
    buckets = [(0, .9, "K/S < 0.90"), (.9, 1.0, "0.90-1.00"), (1.0, 1.1, "1.00-1.10"), (1.1, 9, "> 1.10")]
    grid, decomposition = [], []
    for q in (0.0, 0.002, 0.004, 0.008):
        f = forward_equivalent_surface(raw, q)
        z = minimize(Heston.heston_objective, start, args=(f, spot, 0., "cos", 256), method="SLSQP",
                     bounds=Heston.BOUNDS, constraints=FELLER, options={"maxiter": 300, "ftol": 1e-12})
        model = model_prices("heston", dict(zip(Heston.PARAMETER_NAMES, z.x)), f, spot)
        # Back to quoted contracts: C_q = exp(-qT) C_0(K e^{qT}).
        usd_error = np.exp(-q * f["T"].to_numpy()) * model - f.price_quoted.to_numpy() if q else model - f.price.to_numpy()
        term = ((model - f.price.to_numpy()) / np.maximum(f.vega.to_numpy(), 1e-4)) ** 2
        grid.append({"dividend_yield": q, "heston_vega_scaled_mse": float(z.fun),
                     "heston_price_rmse_usd": float(np.sqrt(np.mean(usd_error ** 2))),
                     "mean_market_iv": float(f.implied_vol.mean())})
        ratio = raw.K.to_numpy() / spot
        for lo, hi, label in buckets:
            mask = (ratio >= lo) & (ratio < hi)
            decomposition.append({"dividend_yield": q, "bucket": label, "contracts": int(mask.sum()),
                                  "share_of_loss": float(term[mask].sum() / term.sum()),
                                  "price_rmse_usd": float(np.sqrt(np.mean(usd_error[mask] ** 2))) if mask.any() else np.nan})
    pd.DataFrame(grid).to_csv(O / "carry_sensitivity.csv", index=False)
    pd.DataFrame(decomposition).to_csv(O / "carry_loss_by_moneyness.csv", index=False)
    bounds = []
    for (T, r), g in raw.groupby(["T", "rate"]):
        deepest = g.loc[g.K.idxmin()]
        bounds.append({"maturity_years": T, "strike": deepest.K, "upper_bound_forward": deepest.K + deepest.price * np.exp(r * T),
                       "forward_q0": spot * np.exp(r * T), "forward_q040": spot * np.exp((r - .004) * T)})
    pd.DataFrame(bounds).to_csv(O / "carry_forward_bounds.csv", index=False)

    # Gold carry implied by COMEX GC futures against the synchronous XAUUSD
    # spot (local licensed snapshot; only the aggregate carries are written).
    from datetime import date
    from barrick_unified.dated_valuation import nss_zero_rate
    futures_file = R / "data/raw/ib_local/20260902T200000Z-gc-futures-options/gc_futures_option_bid_ask.csv"
    anchor = json.loads((R / "data/processed/manifests/gold/gold_spot_anchor_20260902.json").read_text())["value"]
    nss = json.loads((R / "data/processed/manifests/rates/team8_us_treasury_nss_20260902.json").read_text())
    nss = {k: nss.get("parameters", nss)[k] for k in ("beta0", "beta1", "beta2", "beta3", "tau1", "tau2")}
    if futures_file.is_file():
        fut = pd.read_csv(futures_file)[["future_local_symbol", "future_expiry", "future_mid"]].drop_duplicates()
        carry = []
        for row in fut.itertuples():
            e = str(row.future_expiry)
            T = (date(int(e[:4]), int(e[4:6]), int(e[6:])) - date(2026, 9, 2)).days / 365.25
            c = np.log(row.future_mid / anchor) / T
            r = float(nss_zero_rate(nss, np.array([T]))[0])
            carry.append({"future": row.future_local_symbol, "maturity_years": T, "gold_carry": c, "treasury_zero": r,
                          "implied_gld_yield": r - (c - GLD_FEE)})
        pd.DataFrame(carry).to_csv(O / "carry_futures_implied.csv", index=False)
        print(pd.DataFrame(carry).round(5).to_string(index=False))

    # American early-exercise premium of the 64 calls with q = 0.40% (CRR at
    # observed IV); q < r keeps it small but no longer zero by construction.
    f = forward_equivalent_surface(raw, GLD_FEE)
    premia = []
    for row in raw.assign(iv=f.implied_vol.to_numpy()).itertuples():
        steps = 800
        dt = row.T / steps
        u = np.exp(row.iv * np.sqrt(dt))
        d = 1 / u
        prob = (np.exp((row.rate - GLD_FEE) * dt) - d) / (u - d)
        disc = np.exp(-row.rate * dt)
        prices = spot * d ** np.arange(steps, -1, -1) * u ** np.arange(steps + 1)
        american = np.maximum(prices - row.K, 0.0)
        european = american.copy()
        for j in range(steps - 1, -1, -1):
            american = disc * ((1 - prob) * american[:-1] + prob * american[1:])
            european = disc * ((1 - prob) * european[:-1] + prob * european[1:])
            nodes = spot * d ** np.arange(j, -1, -1) * u ** np.arange(j + 1)
            american = np.maximum(american, nodes - row.K)
        premia.append(float(american[0] - european[0]))
    write_json(O / "american_check.json", {"contracts": len(premia), "tree_steps": 800, "dividend_yield": GLD_FEE,
                                           "max_premium_usd": max(premia), "mean_premium_usd": float(np.mean(premia)),
                                           "max_premium_over_price": float(max(p / c for p, c in zip(premia, raw.price))),
                                           "scope": "CRR at observed IV; not a stochastic-volatility American tree"})
    print("American premium max", max(premia))
    print(pd.DataFrame(grid).to_string(index=False))
    print(pd.DataFrame(decomposition).to_string(index=False))
    print(pd.DataFrame(bounds).to_string(index=False))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("stage", choices=["calibration", "carry", "valuation", "paths", "copper", "oos", "all"])
    p.add_argument("--calibration-dir", default="data/processed/team8/calibration_q040_20261024/CC/2026-09-02")
    p.add_argument("--audited-dir", default="data/processed/team8/calibration_q040_audited_20261024")
    p.add_argument("--config", default="data/processed/config/paper_dated_q040_20261024.json")
    p.add_argument("--oos-dir", default="data/processed/team8/oos_q040_20261024")
    p.add_argument("--output-dir", default="outputs/paper_audit_20261024")
    p.add_argument("--figure-dir", default="outputs/img/paper_audit_20261024")
    a = p.parse_args()
    for name in ("calibration_dir", "audited_dir", "output_dir", "figure_dir", "oos_dir"):
        setattr(a, name, str(R / getattr(a, name)))
    Path(a.output_dir).mkdir(parents=True, exist_ok=True)
    if a.stage in ("calibration", "all"):
        stage_calibration(a)
    if a.stage in ("carry", "all"):
        stage_carry(a)
    if a.stage in ("valuation", "all"):
        stage_valuation(a)
    if a.stage == "paths":
        stage_path_validation(a)
    if a.stage in ("copper", "all"):
        stage_copper(a)
    if a.stage in ("oos", "all"):
        stage_oos(a)


if __name__ == "__main__":
    main()
