"""Fresh interpreters must resolve the shared runtime without reference fallbacks."""
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('entrypoint', [
    'utilities/python/pricing/calibrate_surface.py',
    'utilities/python/pricing/calibrate_one_day.py',
    'utilities/python/pricing/oos_validation.py',
    'utilities/python/tools/run_copper_oos.py',
    'utilities/python/tools/calibrate_ib_copper_models.py',
])
def test_standalone_help(entrypoint):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONPATH', None)
    result = subprocess.run([sys.executable, '-B', str(ROOT/entrypoint), '--help'],
                            cwd=ROOT, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert 'usage:' in result.stdout.lower()


def test_oos_dispatch_uses_shared_calibrator(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'utilities/python/pricing'))
    import oos_validation
    import pandas as pd

    calls = []
    monkeypatch.setattr(oos_validation.subprocess, 'run',
                        lambda command, **kwargs: calls.append((command, kwargs)))
    oos_validation.invoke_calibration(ROOT, pd.Timestamp('2026-07-10'),
        Path('surface.csv'), Path('results'), 'CC', 'quick', 104, False)
    command, kwargs = calls[0]
    assert Path(command[1]) == ROOT/'utilities/python/pricing/calibrate_surface.py'
    assert Path(command[1]).is_file()
    assert kwargs['check'] is True
