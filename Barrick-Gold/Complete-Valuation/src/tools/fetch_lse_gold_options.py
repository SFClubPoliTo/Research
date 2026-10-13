"""Fetch the optional LSE GLD chain with the approved manual rate curve.

This is the alternate Team 8 option-source path.  It intentionally does not
request LSE Treasury yields and stops before surface construction, implied
volatility processing, calibration, or figure generation.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from barrick_unified.lse_adapter import (  # noqa: E402
    LSEMarketDataProvider,
    write_private_snapshot,
)
from barrick_unified.team8_rate_curve import (  # noqa: E402
    MANUAL_CURVE_DATE,
    manual_curve_frame,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def infer_snapshot_utc(rows: list[dict[str, Any]]) -> str | None:
    values = [
        str(row["updated_at"])
        for row in rows
        if row.get("updated_at") not in (None, "")
    ]
    if not values:
        return None
    parsed = [datetime.fromisoformat(value.replace("Z", "+00:00")) for value in values]
    return max(parsed).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    run_id = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ-gld-options-manual-curve"
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-dte", type=int, default=1000)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data" / "raw" / "lse_local" / run_id,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing raw run: {output_dir}")

    rows = LSEMarketDataProvider().fetch_gld_option_chain(max_dte=args.max_dte)
    if not rows:
        raise RuntimeError("LSE returned an empty GLD option chain")

    raw_path = output_dir / "gld_option_calls.json"
    curve_path = output_dir / f"manual_yield_curve_{MANUAL_CURVE_DATE}.csv"
    manifest_path = output_dir / "run_manifest.json"
    payload = {
        "provider": "London Strategic Edge",
        "instrument": "GLD call options",
        "snapshot_utc": infer_snapshot_utc(rows),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "request": {"underlying": "GLD", "right": "call", "max_dte": args.max_dte},
        "rows": rows,
    }
    write_private_snapshot(raw_path, payload)
    manual_curve_frame().to_csv(curve_path, index=False)
    manifest = {
        "provider": "London Strategic Edge",
        "option_rows": len(rows),
        "snapshot_utc": payload["snapshot_utc"],
        "rate_curve": {
            "source": "manual_user_supplied",
            "curve_date": MANUAL_CURVE_DATE,
            "fit_status": "not_run_in_acquisition_stage",
        },
        "lse_treasury_yields_requested": False,
        "downstream_status": {
            "surface": "not_run",
            "implied_volatility": "not_run",
            "model_calibration": "not_run",
            'figures': "not_run",
        },
        "files": {
            raw_path.name: {"sha256": sha256_file(raw_path), "bytes": raw_path.stat().st_size},
            curve_path.name: {"sha256": sha256_file(curve_path), "bytes": curve_path.stat().st_size},
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[DONE] LSE GLD calls: {len(rows)}", flush=True)
    print(f"[DONE] local manifest: {manifest_path}", flush=True)
    print("[GATE] surface/calibration/figures were not run", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
