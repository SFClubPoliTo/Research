"""Previous-origin initialization must be chronological and quality guarded."""
import importlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest
from scipy.optimize import OptimizeResult

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'src/pricing'))
    return importlib.import_module('dated_initialization'), importlib.import_module('calibration_core')


def test_latest_successful_strictly_past_only(tmp_path, modules):
    dated, _ = modules
    for day, success in [('2026-07-10',True),('2026-07-13',False),('2026-07-14',True)]:
        (tmp_path/f'{day}.json').write_text(json.dumps(dict(origin=day,model='bates',
            success=success,status='DATED_Q_CALIBRATION_NOT_PHYSICAL_FORECAST')))
    # Invalid future file must never even be parsed.
    (tmp_path/'2026-09-02.json').write_text('future data inaccessible')
    record, source = dated.previous_fit(tmp_path,'2026-07-14','bates')
    assert record['origin'] == source['origin'] == '2026-07-10'
    assert len(source['source_sha256']) == 64
    assert dated.previous_fit(tmp_path,'2026-07-10','bates') == (None,None)


def test_local_failure_and_worsening_request_global_fallback(modules, monkeypatch):
    _, core = modules
    x = np.array([.04,2.,.04,.2,-.5])
    bounds = [(0,1),(.1,10),(0,1),(.01,8),(-.99,.99)]
    objective = lambda y: float(np.sum((y-x)**2))
    monkeypatch.setattr(core,'minimize',lambda *a,**k: OptimizeResult(x=x,fun=0.,success=False))
    assert core.warm_local_fit(objective,x,bounds,(),ftol=1e-7) is None
    monkeypatch.setattr(core,'minimize',lambda *a,**k: OptimizeResult(x=x+[.01,0,0,0,0],fun=0.,success=True))
    assert core.warm_local_fit(objective,x,bounds,(),ftol=1e-7) is None
    assert core.warm_local_fit(objective,np.full(5,np.nan),bounds,(),ftol=1e-7) is None


@pytest.mark.parametrize('model',['Heston','Bates'])
def test_warm_calibration_skips_global_search(model, modules, monkeypatch):
    module = importlib.import_module(model)
    cls = getattr(module,model)
    x = np.array([.04,2.,.04,.2,-.5]+([.2,-.1,.1] if model=='Bates' else []))
    objective_name = 'heston_objective' if model=='Heston' else 'bates_objective'
    monkeypatch.setattr(cls,objective_name,staticmethod(lambda y,*a:float(np.sum((y-x)**2))))
    def forbidden(*args,**kwargs):
        raise AssertionError('Global search should not run for a converged warm fit')
    monkeypatch.setattr(module,'differential_evolution',forbidden)
    frame=pd.DataFrame(dict(K=[100.],T=[1.],rate=[.02],price=[10.],vega=[30.]))
    kwargs={'heston_seed':x[:5]} if model=='Bates' else {}
    result=getattr(cls,'calibrate_heston' if model=='Heston' else 'calibrate_bates')(
        frame,100.,initial_guess=x,return_report=True,**kwargs)
    assert result.warm_start_used and not result.global_search_used
    assert result.global_objective is None
    assert result.objective <= 1e-12


def test_hawkes_uses_prior_point_and_falls_back_on_local_failure(modules, monkeypatch):
    module=importlib.import_module('Hawkes')
    cls=module.ExactHawkesCalibration
    frame=pd.DataFrame(dict(K=[100.],T=[1.],rate=[.02],price=[10.],vega=[30.]))
    bates=np.array([.04,2.,.04,.2,-.5,.2,-.1,.1])
    prior=np.array([.04,2.,.04,.2,-.5,.2,.1,.2,1.,-.1,.1])
    starts=[]
    monkeypatch.setattr(cls,'objective_heston',classmethod(lambda cls,x,*a:1.))
    def local(*a,**kw):
        starts.append(kw['x0'].copy())
        return OptimizeResult(x=kw['x0'],fun=1.,success=True)
    monkeypatch.setattr(module,'minimize',local)
    def forbidden(*a,**kw):
        raise AssertionError('unexpected global search')
    monkeypatch.setattr(module,'differential_evolution',forbidden)
    result=cls.calibrate_heston(frame,100.,bates_seed=bates,hawkes_seed=prior)
    assert result.warm_start_used and not result.global_search_used
    np.testing.assert_allclose(starts[0],prior)
    monkeypatch.setattr(module,'minimize',lambda *a,**kw:OptimizeResult(x=kw['x0'],fun=1.,success=False))
    with pytest.raises(AssertionError,match='unexpected global'):
        cls.calibrate_heston(frame,100.,bates_seed=bates,hawkes_seed=prior)
