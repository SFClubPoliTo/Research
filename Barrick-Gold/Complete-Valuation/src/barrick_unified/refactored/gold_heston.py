"""Frozen Team 8 Heston path adapter."""

from __future__ import annotations

import numpy as np

from barrick_unified.refactored.gold_base import GoldPriceModel, GoldSimulationContext


class HestonGoldModel(GoldPriceModel):
    model_id = "heston"
    label = "Heston"

    def _simulate_fine(self, context: GoldSimulationContext) -> np.ndarray:
        # Calibration files name the vol-of-vol "sigma" (Heston.PARAMETER_NAMES);
        # older hand-written contexts used "xi".  Accept either.
        p = context.parameters
        parameters = tuple(
            float(p[name] if name != "xi" else p.get("xi", p.get("sigma")))
            for name in ("v0", "kappa", "theta", "xi", "rho")
        )
        return context.team8_module.simulate_heston_paths(
            context.start_usd_per_oz,
            context.fine_drift,
            parameters,
            context.grid.fine_dt_years,
            context.n_paths,
            context.seed,
        )[0]
