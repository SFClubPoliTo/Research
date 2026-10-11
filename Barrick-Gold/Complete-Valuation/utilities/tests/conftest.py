"""Keep independently frozen pricing trees isolated between test modules.

Production loaders deliberately reject cross-tree cache contamination. Tests
of old and current freezes must not share their top-level legacy imports;
the rejection itself remains tested within the valuation test module.
"""
import os
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
import sys
import pytest


@pytest.fixture(scope='module',autouse=True)
def isolate_legacy_pricing_imports():
    names={'BatesHawkesExact','Hawkes','Bates','Heston','BnS','Sampling','calibration_core'}
    def relevant(name):
        return name in names or name.startswith('_barrick_frozen_team8_path_simulation_')
    previous={name:module for name,module in list(sys.modules.items()) if relevant(name)}
    old_path=list(sys.path)
    for name in previous:sys.modules.pop(name,None)
    try:
        yield
    finally:
        for name in list(sys.modules):
            if relevant(name):sys.modules.pop(name,None)
        sys.modules.update(previous)
        sys.path[:]=old_path
