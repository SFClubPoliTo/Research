"""Esporta il caso deterministico FCFF senza richiedere i moduli di G3."""

import argparse
import csv
from pathlib import Path

import numpy as np
import yaml

from src.fcff.model import fcff
from src.revenues.model import simulate_revenues


def export_reference(config_path, output_path):
    cfg = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    revenues = simulate_revenues(
        cfg["revenues"]["r0"], np.asarray(cfg["revenues"]["g_path"]),
        sigma=0., n_paths=1, seed=cfg["simulation"]["seed"])
    nopat, reinvest, cashflows = fcff(
        revenues, cfg["revenues"]["r0"], cfg["fcff_parameters"])
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["t", "revenues", "nopat", "reinvest", "fcff"])
        for t in range(revenues.shape[1]):
            writer.writerow([t + 1, revenues[0, t], nopat[0, t],
                             reinvest[0, t], cashflows[0, t]])


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=root / "config/config.yaml")
    parser.add_argument("--output", type=Path, default=root / "output/d07_reference.csv")
    args = parser.parse_args()
    export_reference(args.config, args.output)
    print(f"Caso deterministico salvato in {args.output}")
