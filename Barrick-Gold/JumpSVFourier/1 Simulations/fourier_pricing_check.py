"""Fourier pricing check: Heston and Merton European calls via characteristic functions.

- Heston: full-truncation Euler Monte Carlo with correlated Brownian motions versus the
  little-trap characteristic function (Albrecher et al., 2007) priced with Gil-Pelaez.
- Merton jump-diffusion: the same Gil-Pelaez pricer versus Merton's closed-form series
  and an exact terminal-value Monte Carlo.
"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
from scipy.stats import norm

from simulate_examples import IMG_DIR, OUTPUT_DIR, SEED, write_csv


S0, RATE, MATURITY = 100.0, 0.03, 1.0
STRIKES = np.array([80.0, 90.0, 100.0, 110.0, 120.0])
HESTON = {"v0": 0.045, "kappa": 3.0, "theta": 0.045, "xi": 0.32, "rho": -0.7}
MERTON = {"sigma": 0.18, "lam": 2.2, "mu_j": -0.09, "sigma_j": 0.05}
N_PATHS, N_STEPS = 200_000, 252


def heston_cf(u: complex, v0: float, kappa: float, theta: float, xi: float, rho: float) -> complex:
    """Characteristic function of log S_T under Heston, little-trap formulation."""
    iu = 1j * u
    beta = kappa - rho * xi * iu
    d = np.sqrt(beta**2 + xi**2 * (iu + u**2))
    g = (beta - d) / (beta + d)
    exp_dt = np.exp(-d * MATURITY)
    c = RATE * iu * MATURITY + kappa * theta / xi**2 * (
        (beta - d) * MATURITY - 2.0 * np.log((1.0 - g * exp_dt) / (1.0 - g))
    )
    dd = (beta - d) / xi**2 * (1.0 - exp_dt) / (1.0 - g * exp_dt)
    return np.exp(c + dd * v0 + iu * math.log(S0))


def merton_kappa() -> float:
    return math.exp(MERTON["mu_j"] + 0.5 * MERTON["sigma_j"] ** 2) - 1.0


def merton_cf(u: complex, sigma: float, lam: float, mu_j: float, sigma_j: float) -> complex:
    """Characteristic function of log S_T under compensated Merton jump-diffusion."""
    drift = math.log(S0) + (RATE - 0.5 * sigma**2 - lam * merton_kappa()) * MATURITY
    jump = lam * MATURITY * (np.exp(1j * u * mu_j - 0.5 * sigma_j**2 * u**2) - 1.0)
    return np.exp(1j * u * drift - 0.5 * sigma**2 * u**2 * MATURITY + jump)


def gil_pelaez_call(cf, strike: float, upper: float = 200.0) -> float:
    """C = S0 P1 - K e^{-rT} P2 with P1, P2 from Gil-Pelaez inversion of the log-price CF."""
    log_k = math.log(strike)
    forward = cf(-1j)  # = S0 e^{rT} under the risk-neutral measure

    def p1_integrand(u: float) -> float:
        return (np.exp(-1j * u * log_k) * cf(u - 1j) / (1j * u * forward)).real

    def p2_integrand(u: float) -> float:
        return (np.exp(-1j * u * log_k) * cf(u) / (1j * u)).real

    p1 = 0.5 + quad(p1_integrand, 1e-8, upper, limit=500)[0] / math.pi
    p2 = 0.5 + quad(p2_integrand, 1e-8, upper, limit=500)[0] / math.pi
    return S0 * p1 - strike * math.exp(-RATE * MATURITY) * p2


def black_scholes_call(spot: float, strike: float, rate: float, sigma: float, maturity: float) -> float:
    d1 = (math.log(spot / strike) + (rate + 0.5 * sigma**2) * maturity) / (sigma * math.sqrt(maturity))
    d2 = d1 - sigma * math.sqrt(maturity)
    return spot * norm.cdf(d1) - strike * math.exp(-rate * maturity) * norm.cdf(d2)


def merton_series_call(strike: float, n_terms: int = 60) -> float:
    """Merton (1976) closed form: Poisson mixture of Black-Scholes prices."""
    kappa = merton_kappa()
    lam_prime = MERTON["lam"] * (1.0 + kappa)
    price = 0.0
    for n in range(n_terms):
        sigma_n = math.sqrt(MERTON["sigma"] ** 2 + n * MERTON["sigma_j"] ** 2 / MATURITY)
        rate_n = RATE - MERTON["lam"] * kappa + n * math.log(1.0 + kappa) / MATURITY
        weight = math.exp(-lam_prime * MATURITY + n * math.log(lam_prime * MATURITY) - math.lgamma(n + 1))
        price += weight * black_scholes_call(S0, strike, rate_n, sigma_n, MATURITY)
    return price


def heston_mc(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Full-truncation Euler for (log S, v); returns terminal prices and two sample paths."""
    p = HESTON
    dt = MATURITY / N_STEPS
    log_s = np.full(N_PATHS, math.log(S0))
    v = np.full(N_PATHS, p["v0"])
    sample_s, sample_v = [np.exp(log_s[:3])], [v[:3].copy()]
    for _ in range(N_STEPS):
        z_v = rng.standard_normal(N_PATHS)
        z_s = p["rho"] * z_v + math.sqrt(1.0 - p["rho"] ** 2) * rng.standard_normal(N_PATHS)
        v_pos = np.maximum(v, 0.0)
        log_s += (RATE - 0.5 * v_pos) * dt + np.sqrt(v_pos * dt) * z_s
        v += p["kappa"] * (p["theta"] - v_pos) * dt + p["xi"] * np.sqrt(v_pos * dt) * z_v
        sample_s.append(np.exp(log_s[:3]))
        sample_v.append(np.maximum(v[:3], 0.0))
    return np.exp(log_s), np.array(sample_s), np.array(sample_v)


def merton_mc(rng: np.random.Generator) -> np.ndarray:
    """Exact terminal sampling: N ~ Poisson(lam T), jump sum ~ N(n mu_J, n sigma_J^2)."""
    p = MERTON
    n_jumps = rng.poisson(p["lam"] * MATURITY, size=N_PATHS)
    jumps = p["mu_j"] * n_jumps + p["sigma_j"] * np.sqrt(n_jumps) * rng.standard_normal(N_PATHS)
    drift = (RATE - 0.5 * p["sigma"] ** 2 - p["lam"] * merton_kappa()) * MATURITY
    diffusion = p["sigma"] * math.sqrt(MATURITY) * rng.standard_normal(N_PATHS)
    return S0 * np.exp(drift + diffusion + jumps)


def mc_call(terminal: np.ndarray, strike: float) -> tuple[float, float]:
    payoff = math.exp(-RATE * MATURITY) * np.maximum(terminal - strike, 0.0)
    return float(payoff.mean()), float(payoff.std(ddof=1) / math.sqrt(payoff.size))


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED + 1)

    # Sanity check of the Fourier pricer: Heston with xi -> 0 and v0 = theta is Black-Scholes.
    bs_limit = gil_pelaez_call(lambda u: heston_cf(u, 0.045, 3.0, 0.045, 1e-3, 0.0), 100.0)
    bs_exact = black_scholes_call(S0, 100.0, RATE, math.sqrt(0.045), MATURITY)
    print(f"Heston(xi->0) Fourier {bs_limit:.6f} vs Black-Scholes {bs_exact:.6f}")

    heston_terminal, sample_s, sample_v = heston_mc(rng)
    merton_terminal = merton_mc(rng)

    rows, columns = [], ["model", "strike", "fourier_cf_price", "reference_method", "reference_price", "reference_std_error", "abs_diff", "diff_over_se"]
    for strike in STRIKES:
        heston_fourier = gil_pelaez_call(lambda u: heston_cf(u, **HESTON), strike)
        merton_fourier = gil_pelaez_call(lambda u: merton_cf(u, **MERTON), strike)
        h_mc, h_se = mc_call(heston_terminal, strike)
        m_mc, m_se = mc_call(merton_terminal, strike)
        m_series = merton_series_call(strike)
        rows.append(["Heston", strike, heston_fourier, "MC full-truncation Euler", h_mc, h_se, abs(h_mc - heston_fourier), (h_mc - heston_fourier) / h_se])
        rows.append(["Merton", strike, merton_fourier, "closed-form series", m_series, "", abs(m_series - merton_fourier), ""])
        rows.append(["Merton", strike, merton_fourier, "MC exact terminal", m_mc, m_se, abs(m_mc - merton_fourier), (m_mc - merton_fourier) / m_se])
    rows.append(["Heston xi->0", 100.0, bs_limit, "Black-Scholes sigma=sqrt(theta)", bs_exact, "", abs(bs_limit - bs_exact), ""])
    write_csv(OUTPUT_DIR / "fourier_pricing_check.csv", columns, np.array(rows, dtype=object))

    time = np.linspace(0.0, MATURITY, N_STEPS + 1)
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.4))
    palette = ["#255f85", "#6c8f3d", "#b73f32"]
    for index, color in enumerate(palette):
        axes[0].plot(time, sample_s[:, index], color=color, linewidth=1.4)
        axes[1].plot(time, sample_v[:, index], color=color, linewidth=1.4)
    axes[0].set_title("Heston price paths (full-truncation Euler)")
    axes[0].set_xlabel("Years")
    axes[0].set_ylabel("Price index")
    axes[1].axhline(HESTON["theta"], color="#222222", linestyle="--", linewidth=1.0, label="theta")
    axes[1].set_title("Heston variance paths")
    axes[1].set_xlabel("Years")
    axes[1].set_ylabel("Variance")
    axes[1].legend(frameon=False)

    for model, marker, offset in [("Heston", "o", -0.6), ("Merton", "s", 0.6)]:
        mc_rows = [row for row in rows if row[0] == model and row[3].startswith("MC")]
        diffs = np.array([row[4] - row[2] for row in mc_rows])
        ses = np.array([row[5] for row in mc_rows])
        axes[2].errorbar(STRIKES + offset, diffs, yerr=1.96 * ses, fmt=marker, capsize=3, label=f"{model}: MC - Fourier (95% CI)")
    series = np.array([row[4] - row[2] for row in rows if row[3] == "closed-form series"])
    axes[2].plot(STRIKES, series, "k^", label="Merton: series - Fourier")
    axes[2].axhline(0.0, color="#222222", linewidth=0.8)
    axes[2].set_title("Pricing error versus Fourier price")
    axes[2].set_xlabel("Strike")
    axes[2].set_ylabel("Call price difference")
    axes[2].legend(frameon=False, fontsize=8)
    for axis in axes:
        axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "fourier_pricing_check.png", dpi=220)
    plt.close(fig)

    for model, strike, fourier, method, reference, *_ in rows:
        print(f"{model:13s} K={strike:6.1f}  Fourier {float(fourier):10.6f}  {method}: {float(reference):10.6f}")


if __name__ == "__main__":
    main()
