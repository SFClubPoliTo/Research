"""Estimate a dated GLD P-drift diagnostic; no corporate valuation output."""
from pathlib import Path
import sys,json,hashlib
from dataclasses import asdict
import pandas as pd
import numpy as np
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file());sys.path.insert(0,str(ROOT/'src'))
from barrick_unified.physical_gbm import fit_gbm,predictive_log_score

def main():
    raw=ROOT/'data/raw/ib_local/physical_history_20261005/gld_rth.csv'
    qfile=ROOT/'data/processed/physical_measure/q_reference_20260902/black_scholes.json'
    d=pd.read_csv(raw);d['date']=pd.to_datetime(d.date);d=d[d.date<=pd.Timestamp('2026-09-02')].sort_values('date')
    r=np.diff(np.log(d.close));dt=d.date.diff().dt.total_seconds().to_numpy()[1:]/(365.25*86400)
    q=json.loads(qfile.read_text());fixed=fit_gbm(r,dt,sigma_q=q['parameters']['sigma']);free=fit_gbm(r,dt)
    oos=[]
    for i in range(252,len(r)):
        # Only historical observations before this forecast; no September Q parameters.
        f=fit_gbm(r[:i],dt[:i]);price=float(d.close.iloc[i]);target=float(d.close.iloc[i+1])
        oos.append(dict(origin=str(d.date.iloc[i].date()),target=str(d.date.iloc[i+1].date()),log_score=float(predictive_log_score(r[i],dt[i],f)),squared_error=(price*np.exp(f.arithmetic_drift*dt[i])-target)**2,random_walk_squared_error=(price-target)**2))
    o=pd.DataFrame(oos)
    result=dict(status='DIAGNOSTIC_NOT_ADMITTED_TO_BARRICK_DCF',underlying='GLD_USD_PER_SHARE',cutoff='2026-09-02',
                historical_mle=asdict(free),fixed_current_Q_diffusion=asdict(fixed),
                fixed_Q_drift_95_interval=[fixed.arithmetic_drift-1.96*fixed.drift_standard_error,fixed.arithmetic_drift+1.96*fixed.drift_standard_error],
                historical_only_oos=dict(n=len(o),rmse=float(np.sqrt(o.squared_error.mean())),random_walk_rmse=float(np.sqrt(o.random_walk_squared_error.mean())),mean_log_score=float(o.log_score.mean())),
                limitations=['Fixed-Q result is in-sample and uses current calibration; not used in historical OOS.', 'GLD is not gold USD/oz; basis model required.', 'Constant drift and diffusion assume temporal stability; standard error conditions on model.', 'Other three model families not yet physically estimated.'],
                hashes={str(raw.relative_to(ROOT)):hashlib.sha256(raw.read_bytes()).hexdigest(),str(qfile):hashlib.sha256(qfile.read_bytes()).hexdigest()})
    out=ROOT/'outputs/physical_measure/20261005-gbm-diagnostic';out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2)[:2100])
if __name__=='__main__':main()
