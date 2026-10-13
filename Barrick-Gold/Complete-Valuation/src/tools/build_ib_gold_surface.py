"""Build the approval-gated observed IV surface from the local IB snapshot."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib import colormaps
import matplotlib.tri as mtri
import pandas as pd


ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from barrick_unified.ib_gold_surface import (  # noqa: E402
    SurfaceFilterConfig,
    build_observed_surface,
    select_chebyshev_nodes,
)
from barrick_unified.team8_rate_curve import MANUAL_CURVE_DATE  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def render_surface(selected: pd.DataFrame, output: Path) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    figure = plt.figure(figsize=(20, 10.8), facecolor="#f4f5f7")
    grid = figure.add_gridspec(1, 2, width_ratios=(1.12, 1.0), wspace=0.24)
    axis_3d = figure.add_subplot(grid[0, 0], projection="3d")
    axis_2d = figure.add_subplot(grid[0, 1])

    x = selected["moneyness_k_over_f"].to_numpy(dtype=float)
    y = selected["maturity_years_act36525"].to_numpy(dtype=float)
    z = selected["implied_vol"].to_numpy(dtype=float) * 100.0
    triangulation = mtri.Triangulation(x, y)
    surface = axis_3d.plot_trisurf(
        triangulation,
        z,
        cmap="viridis",
        alpha=0.82,
        linewidth=0.25,
        edgecolor="#334155",
        antialiased=True,
    )
    axis_3d.scatter(
        x,
        y,
        z,
        s=26,
        c="#111827",
        depthshade=False,
        label=f"{len(selected)} observed Chebyshev nodes",
    )
    axis_3d.set_xlabel("Moneyness (K / F)", labelpad=10)
    axis_3d.set_ylabel("Maturity (years)", labelpad=10)
    axis_3d.set_zlabel("Black-76 implied volatility (%)", labelpad=10)
    axis_3d.set_title("Observed COMEX nodes — Chebyshev 8×8", pad=18)
    axis_3d.view_init(elev=27, azim=-126)
    axis_3d.legend(loc="upper left")
    colorbar = figure.colorbar(surface, ax=axis_3d, shrink=0.58, pad=0.10)
    colorbar.set_label("Pointwise implied volatility (%)")

    expiries = sorted(selected["option_expiry"].astype(str).unique())
    colors = colormaps["viridis"].resampled(len(expiries))
    for color_index, expiry in enumerate(expiries):
        group = selected.loc[
            selected["option_expiry"].astype(str).eq(expiry)
        ].sort_values("moneyness_k_over_f")
        label = f"{expiry[:4]}-{expiry[4:6]}-{expiry[6:]} (n={len(group)})"
        axis_2d.plot(
            group["moneyness_k_over_f"],
            group["implied_vol"] * 100.0,
            marker="o",
            markersize=4.8,
            linewidth=1.6,
            color=colors(color_index),
            label=label,
        )
    axis_2d.set_xlabel("Moneyness (K / F)")
    axis_2d.set_ylabel("Black-76 implied volatility (%)")
    axis_2d.set_title("Selected real quotes by option expiry")
    axis_2d.legend(ncol=2, fontsize=8.7, loc="best")

    figure.suptitle(
        "Team 8 — COMEX Gold futures-option IV surface (no stochastic-model calibration)\n"
        "MARKET DATE: 2026-09-02 | SNAPSHOT: 20:00:00 UTC | "
        "64 CHEBYSHEV NODES | IB API",
        fontsize=17,
        fontweight="bold",
        y=0.985,
    )
    figure.text(
        0.5,
        0.018,
        "Historical bid/ask midpoints; OTM calls and puts; matching GC future by expiry. "
        "Black-76 inversion with manual 2026-09-02 NSS rates. No Heston/Bates/Hawkes fit was run.",
        ha="center",
        fontsize=10.5,
        color="#374151",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        output,
        dpi=220,
        bbox_inches="tight",
        facecolor=figure.get_facecolor(),
    )
    plt.close(figure)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT
        / "data/raw/ib_local/20260902T200000Z-gc-futures-options/gc_futures_option_bid_ask.csv",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-relative-spread", type=float, default=0.20)
    parser.add_argument("--max-quote-age-seconds", type=float, default=120.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = SurfaceFilterConfig(
        max_relative_spread=args.max_relative_spread,
        max_quote_age_seconds=args.max_quote_age_seconds,
    )
    quotes = pd.read_csv(args.input)
    audit, metadata = build_observed_surface(quotes, config)
    selected = select_chebyshev_nodes(
        audit,
        config.chebyshev_maturities,
        config.chebyshev_moneyness,
    )

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / "SURFACE_FINALE_TEAM8_IB_COMEX_2026-09-02.png"
    selected_path = output_dir / "ib_comex_chebyshev_64_selected_2026-09-02.csv"
    summary_path = output_dir / "ib_comex_surface_audit_2026-09-02.json"
    for path in (image_path, selected_path, summary_path):
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")

    selected.to_csv(selected_path, index=False)
    render_surface(selected, image_path)
    metadata.update(
        {
            "provider": "IB API",
            "instrument": "standard monthly COMEX Gold futures options (OG)",
            "underlying": "matching COMEX Gold future (GC) for each option expiry",
            "market_date": "2026-09-02",
            "snapshot_utc": "2026-09-02T20:00:00Z",
            "option_price": "historical bid/ask midpoint in futures quote units",
            "pointwise_iv_method": "Black-76 bounded scalar inversion",
            "option_selection": "OTM puts below F and OTM calls at/above F",
            "rate_curve_date": MANUAL_CURVE_DATE,
            "rate_curve_input": (
                "manual user-supplied par-yield nodes used directly in calibrate_nss_ols"
            ),
            "stochastic_model_calibration_called": False,
            "selected_nodes": int(len(selected)),
            "selected_unique_contracts": int(selected["option_con_id"].nunique()),
            "selected_expiries": int(selected["option_expiry"].nunique()),
            "selected_rights": {
                str(key): int(value)
                for key, value in selected["right"].value_counts().items()
            },
            "generated_at_utc": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "source_file": str(args.input.resolve()),
            "source_sha256": sha256_file(args.input),
            "artifacts": {
                selected_path.name: sha256_file(selected_path),
                image_path.name: sha256_file(image_path),
            },
        }
    )
    summary_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "eligible_rows": metadata["eligible_rows"],
                "selected_nodes": metadata["selected_nodes"],
                "selected_expiries": metadata["selected_expiries"],
                "image": str(image_path),
                "summary": str(summary_path),
            },
            indent=2,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
