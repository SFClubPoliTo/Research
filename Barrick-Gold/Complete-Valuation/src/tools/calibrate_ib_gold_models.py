"""Calibrate the four Team 8 models to the full IB COMEX Gold cross-section."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd


ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from barrick_unified.ib_gold_calibration import (  # noqa: E402
    deterministic_strike_holdout,
    run_calibrations,
    static_arbitrage_audit,
)
from barrick_unified.ib_gold_surface import (  # noqa: E402
    SurfaceFilterConfig,
    build_observed_surface,
    normalized_call_surface,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT
        / "data/raw/ib_local/20260902T200000Z-gc-futures-options/gc_futures_option_bid_ask.csv",
    )
    parser.add_argument(
        "--team8-source",
        type=Path,
        default=ROOT / 'src/reference/team-8',
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--heston-maxiter", type=int, default=50)
    parser.add_argument("--bates-maxiter", type=int, default=60)
    parser.add_argument("--hawkes-maxiter", type=int, default=20)
    parser.add_argument("--popsize", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260902)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Refusing to overwrite calibration run: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    quotes = pd.read_csv(args.input)
    row_audit, filter_metadata = build_observed_surface(
        quotes, SurfaceFilterConfig()
    )
    surface = normalized_call_surface(row_audit)
    arbitrage = static_arbitrage_audit(surface)
    if not arbitrage["passed"]:
        raise RuntimeError(f"Static-arbitrage gate failed: {arbitrage}")
    train, holdout = deterministic_strike_holdout(surface)

    results, metrics, diagnostics = run_calibrations(
        surface,
        args.team8_source,
        heston_maxiter=args.heston_maxiter,
        bates_maxiter=args.bates_maxiter,
        hawkes_maxiter=args.hawkes_maxiter,
        popsize=args.popsize,
        seed=args.seed,
    )

    surface_path = output_dir / "ib_comex_full_calibration_surface.csv"
    diagnostics_path = output_dir / "ib_comex_model_diagnostics.csv"
    metrics_path = output_dir / "ib_comex_calibration_metrics.csv"
    parameters_path = output_dir / "ib_comex_calibrated_parameters.json"
    manifest_path = output_dir / "run_manifest.json"
    surface.to_csv(surface_path, index=False)
    diagnostics.to_csv(diagnostics_path, index=False)
    metrics.to_csv(metrics_path, index=False)
    parameters_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    manifest = {
        "status": "IB_COMEX_TEAM8_FULL_SAMPLE_CALIBRATION",
        "provider": "IB API",
        "market_date": "2026-09-02",
        "snapshot_utc": "2026-09-02T20:00:00Z",
        "instrument": "standard monthly COMEX Gold futures options (OG)",
        "normalization": (
            "OTM puts/calls converted by futures put-call parity and divided by "
            "discount_factor * matching_GC_future"
        ),
        "calibration_sample": "all eligible OTM quotes; not the 64 plotted nodes",
        "input_rows": int(len(quotes)),
        "eligible_rows": int(len(surface)),
        "maturities": int(surface["T"].nunique()),
        "rights": {
            str(key): int(value) for key, value in surface["right"].value_counts().items()
        },
        "strike_holdout_design": {
            "purpose": "reserved-strike interpolation audit; full-sample parameters remain primary",
            "training_rows": int(len(train)),
            "holdout_rows": int(len(holdout)),
            "every": 5,
            "offset": 2,
            "calibration_status": "design_only_not_refitted_in_this_run",
        },
        "surface_filter": filter_metadata,
        "static_arbitrage": arbitrage,
        "optimizer": {
            "seed": args.seed,
            "heston_maxiter": args.heston_maxiter,
            "bates_maxiter": args.bates_maxiter,
            "hawkes_maxiter": args.hawkes_maxiter,
            "popsize": args.popsize,
        },
        "models": results,
        "metrics": metrics.to_dict(orient="records"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {
            "path": str(args.input.resolve()),
            "sha256": sha256_file(args.input),
        },
        "team8_source": str(args.team8_source.resolve()),
        "files": {},
    }
    manifest["files"] = {
        path.name: {"sha256": sha256_file(path), "bytes": path.stat().st_size}
        for path in (surface_path, diagnostics_path, metrics_path, parameters_path)
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(metrics.to_string(index=False), flush=True)
    print(f"[DONE] {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
