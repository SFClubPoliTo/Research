"""Fetch the approved Team 8 COMEX Gold option snapshot from the IB API."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
SRC = ROOT / "utilities/python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from barrick_unified.ib_gold_adapter import (  # noqa: E402
    IBGoldFuturesOptionProvider,
    IBGoldSnapshotConfig,
    write_snapshot,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7497)
    parser.add_argument("--client-id", type=int, default=92)
    parser.add_argument("--snapshot-utc", default="2026-09-02T20:00:00Z")
    parser.add_argument("--max-maturities", type=int, default=9)
    parser.add_argument("--max-strikes", type=int, default=25)
    parser.add_argument("--log-moneyness-limit", type=float, default=0.20)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data" / "raw" / "ib_local" / "20260902T200000Z-gc-futures-options",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = IBGoldSnapshotConfig(
        host=args.host,
        port=args.port,
        client_id=args.client_id,
        snapshot_utc=args.snapshot_utc,
        max_maturities=args.max_maturities,
        max_strikes=args.max_strikes,
        log_moneyness_limit=args.log_moneyness_limit,
    )
    quotes, audit, metadata = IBGoldFuturesOptionProvider(config).collect()
    manifest = write_snapshot(args.output_dir, quotes, audit, metadata)
    print(f"[DONE] valid quotes: {len(quotes)}", flush=True)
    print(f"[DONE] maturities: {quotes['option_expiry'].nunique()}", flush=True)
    print(f"[DONE] local manifest: {manifest}", flush=True)
    print("[GATE] surface/calibration/figures were not run", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
