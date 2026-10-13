"""Gold-price models. These classes never own production, costs or DCF."""

from barrick_unified.refactored.gold_base import GoldPathResult, GoldPriceModel, GoldSimulationContext
from barrick_unified.refactored.gold_registry import GoldModelRegistry, build_frozen_team8_registry

__all__ = [
    "GoldModelRegistry",
    "GoldPathResult",
    "GoldPriceModel",
    "GoldSimulationContext",
    "build_frozen_team8_registry",
]
