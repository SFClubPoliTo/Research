"""Corrected gold-path engines for the dated valuation clock.

The frozen Team 8 adapter (``data/raw/source_freezes/team-8-current/
path_simulation.py``) is kept byte-for-byte for replay of historical runs.  It
clips the stored variance state and holds the Hawkes intensity constant over a
step.  This module is used by every run on the dated clock:

* full truncation (Lord, Koekkoek and van Dijk, 2010): the variance state is
  carried unclipped and only ``max(v, 0)`` enters drift and diffusion;
* Hawkes intensity decays exactly between steps; the jump count of a step is
  Poisson with the exact integrated baseline intensity, and the drift is
  compensated with that same integral, so each step is a martingale
  conditional on the state at its start;
* jump sizes for ``n`` jumps are N(n mu_J, n sigma_J^2).

All engines take one drift per step (``rates``) and return paths including the
time-zero column.  Correctness is checked against the COS prices in
``src/pricing`` by ``validate_against_cos``.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np


def _inputs(start: float, rates: Sequence[float], dt: float, n_paths: int) -> np.ndarray:
    rate_array = np.asarray(rates, dtype=float)
    if start <= 0 or dt <= 0 or n_paths <= 0 or rate_array.ndim != 1:
        raise ValueError("invalid path-simulation inputs")
    if not np.all(np.isfinite(rate_array)):
        raise ValueError("rates must be finite")
    return rate_array


def _correlated_normals(rng: np.random.Generator, n_paths: int, rho: float) -> tuple[np.ndarray, np.ndarray]:
    if not -1.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [-1, 1]")
    z_price = rng.standard_normal(n_paths)
    z_variance = rho * z_price + np.sqrt(max(0.0, 1.0 - rho * rho)) * rng.standard_normal(n_paths)
    return z_price, z_variance


def _jump_log(rng: np.random.Generator, counts: np.ndarray, mu_jump: float, sigma_jump: float) -> np.ndarray:
    return counts * mu_jump + np.sqrt(counts) * sigma_jump * rng.standard_normal(counts.shape[0])


def simulate_gbm_paths(start, rates, sigma, dt, n_paths, seed):
    rate_array = _inputs(start, rates, dt, n_paths)
    if sigma < 0:
        raise ValueError("sigma must be non-negative")
    rng = np.random.default_rng(seed)
    shocks = rng.standard_normal((n_paths, rate_array.size))
    increments = (rate_array - 0.5 * sigma * sigma) * dt + sigma * np.sqrt(dt) * shocks
    log_paths = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(increments, axis=1)], axis=1)
    return start * np.exp(log_paths)


def _stochastic_volatility_paths(start, rates, v0, kappa, theta, xi, rho, dt, n_paths, seed,
                                 jump_step=None):
    """Shared Euler loop; ``jump_step(rng, state) -> (jump_log, compensator_dt)``."""
    rate_array = _inputs(start, rates, dt, n_paths)
    rng = np.random.default_rng(seed)
    n_steps = rate_array.size
    log_price = np.zeros((n_paths, n_steps + 1))
    variance = np.empty((n_paths, n_steps + 1))
    variance[:, 0] = v0
    root_dt = np.sqrt(dt)
    for step, rate in enumerate(rate_array):
        z_price, z_variance = _correlated_normals(rng, n_paths, rho)
        v_pos = np.maximum(variance[:, step], 0.0)
        jumps, compensator_dt = (0.0, 0.0) if jump_step is None else jump_step(rng, step)
        log_price[:, step + 1] = (
            log_price[:, step]
            + (rate - 0.5 * v_pos) * dt
            - compensator_dt
            + np.sqrt(v_pos) * root_dt * z_price
            + jumps
        )
        # Full truncation: the stored state may become negative.
        variance[:, step + 1] = (
            variance[:, step]
            + kappa * (theta - v_pos) * dt
            + xi * np.sqrt(v_pos) * root_dt * z_variance
        )
    return start * np.exp(log_price), variance


def simulate_heston_paths(start, rates, parameters, dt, n_paths, seed):
    v0, kappa, theta, xi, rho = map(float, parameters)
    return _stochastic_volatility_paths(start, rates, v0, kappa, theta, xi, rho, dt, n_paths, seed)


def simulate_bates_paths(start, rates, parameters, dt, n_paths, seed):
    v0, kappa, theta, xi, rho, intensity, mu_jump, sigma_jump = map(float, parameters)
    if intensity < 0 or sigma_jump < 0:
        raise ValueError("jump intensity and dispersion must be non-negative")
    mean_jump = np.exp(mu_jump + 0.5 * sigma_jump**2) - 1.0

    def jump_step(rng, _step):
        counts = rng.poisson(intensity * dt, n_paths)
        return _jump_log(rng, counts, mu_jump, sigma_jump), intensity * mean_jump * dt

    return _stochastic_volatility_paths(start, rates, v0, kappa, theta, xi, rho, dt, n_paths, seed, jump_step)


def simulate_full_hawkes_paths(start, rates, parameters: Mapping[str, float], dt, n_paths, seed):
    p = {name: float(value) for name, value in parameters.items()}
    beta = p["beta"]
    alpha = p.get("alpha", p["branching_ratio"] * beta)
    if beta <= 0 or alpha < 0 or p["sigma_J"] < 0 or not alpha < beta:
        raise ValueError("invalid or non-stationary Hawkes parameters")
    mean_jump = np.exp(p["mu_J"] + 0.5 * p["sigma_J"] ** 2) - 1.0
    decay = np.exp(-beta * dt)
    lam_bar = p["lambda_bar"]
    n_steps = np.asarray(rates).size
    intensity = np.empty((n_paths, n_steps + 1))
    intensity[:, 0] = max(p["lambda0"], 0.0)

    def jump_step(rng, step):
        lam = intensity[:, step]
        # Exact integral of the deterministic decay over the step.
        integrated = lam_bar * dt + (lam - lam_bar) * (1.0 - decay) / beta
        counts = rng.poisson(integrated)
        intensity[:, step + 1] = lam_bar + (lam - lam_bar) * decay + alpha * counts
        return _jump_log(rng, counts, p["mu_J"], p["sigma_J"]), integrated * mean_jump

    paths, variance = _stochastic_volatility_paths(
        start, rates, p["v0"], p["kappa"], p["theta"], p.get("xi", p.get("sigma")), p["rho"],
        dt, n_paths, seed, jump_step,
    )
    return paths, variance, intensity


def simulate_model(model_id: str, parameters: Mapping[str, float], start: float,
                   rates: Sequence[float], dt: float, n_paths: int, seed: int) -> np.ndarray:
    """Return price paths (with time-zero column) for one of the four engines."""
    if model_id == "black_scholes":
        return simulate_gbm_paths(start, rates, float(parameters["sigma"]), dt, n_paths, seed)
    if model_id == "heston":
        names = ("v0", "kappa", "theta", "sigma", "rho")
        values = [parameters.get("xi", parameters.get("sigma")) if n == "sigma" else parameters[n] for n in names]
        return simulate_heston_paths(start, rates, values, dt, n_paths, seed)[0]
    if model_id == "bates_poisson":
        names = ("v0", "kappa", "theta", "sigma", "rho", "lambd", "mu_J", "sigma_J")
        return simulate_bates_paths(start, rates, [parameters[n] for n in names], dt, n_paths, seed)[0]
    if model_id == "full_bates_hawkes":
        return simulate_full_hawkes_paths(start, rates, parameters, dt, n_paths, seed)[0]
    raise ValueError(f"unknown gold model {model_id}")


def validate_against_cos(parameters_by_model: Mapping[str, Mapping[str, float]],
                         maturities=(1.0, 3.0), rate=0.04, n_paths=16384, n_batches=8,
                         steps_per_year=365, seed=20261024) -> list[dict[str, float]]:
    """MC call prices and forward martingale vs the COS pricers, per model.

    Standard errors come from ``n_batches`` independently seeded batches
    (batch means), which stays reliable when self-exciting jumps make the
    payoff distribution heavy-tailed and a single-sample SE is too small.
    """
    import sys
    from pathlib import Path

    pricing = str(Path(__file__).resolve().parents[1] / "pricing")
    if pricing not in sys.path:
        sys.path.insert(0, pricing)
    from BnS import BnS
    from Heston import Heston
    from Bates import Bates
    from BatesHawkesExact import BatesHawkesExact

    start = 100.0
    strikes = np.array([80.0, 100.0, 120.0])
    rows = []
    for model_id, p in parameters_by_model.items():
        for T in maturities:
            n_steps = int(round(T * steps_per_year))
            dt = T / n_steps
            terminal = np.stack([
                simulate_model(model_id, p, start, np.full(n_steps, rate), dt, n_paths, seed + batch)[:, -1]
                for batch in range(n_batches)
            ])
            discount = np.exp(-rate * T)
            forward_batches = terminal.mean(axis=1) * discount / start - 1.0
            forward_error = forward_batches.mean()
            forward_se = forward_batches.std(ddof=1) / np.sqrt(n_batches)
            if model_id == "black_scholes":
                exact = np.array([BnS.bs_call_price(start, k, T, rate, p["sigma"]) for k in strikes])
            elif model_id == "heston":
                exact = Heston.heston_prices_cos(start, strikes, T, p["v0"], p["kappa"], p["theta"],
                                                 p.get("xi", p.get("sigma")), p["rho"], rate, 0.0, N=512)
            elif model_id == "bates_poisson":
                exact = Bates.bates_prices_cos(start, strikes, T, *[p[n] for n in Bates.PARAMETER_NAMES],
                                               rate, 0.0, N=512)
            else:
                alpha = p.get("alpha", p["branching_ratio"] * p["beta"])
                exact = BatesHawkesExact.hawkes_price_cos(
                    start, strikes, T, p["v0"], p["kappa"], p["theta"], p.get("xi", p.get("sigma")), p["rho"],
                    p["lambda0"], p["lambda_bar"], alpha, p["beta"], p["mu_J"], p["sigma_J"], rate, 0.0, N=512)
            for strike, price in zip(strikes, np.asarray(exact, dtype=float)):
                batch_prices = (discount * np.maximum(terminal - strike, 0.0)).mean(axis=1)
                mc = float(batch_prices.mean())
                se = float(batch_prices.std(ddof=1) / np.sqrt(n_batches))
                rows.append({"model": model_id, "maturity_years": T, "strike": float(strike),
                             "paths": n_paths * n_batches, "batches": n_batches,
                             "cos_price": float(price), "mc_price": mc, "mc_se": se,
                             "z_score": (mc - float(price)) / se,
                             "forward_relative_error": float(forward_error),
                             "forward_z_score": float(forward_error / forward_se)})
    return rows
