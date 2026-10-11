"""Exploratory fixed-Q physical fits on GLD; no DCF admission or OOS claim."""
from pathlib import Path
import sys,json,time,xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from scipy.optimize import minimize
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file());sys.path.insert(0,str(ROOT/'src'))
from barrick_unified.physical_filter import physical_filter

def load_training():
    d=pd.read_csv(ROOT/'data/raw/ib_local/physical_history_20261005/gld_rth.csv')
    d['date']=pd.to_datetime(d.date);d=d[d.date<='2026-09-02'].sort_values('date')
    rates=[]
    for p in (ROOT/'data/raw/treasury_public/physical_history_20261005').glob('*.xml'):
        root=ET.fromstring(p.read_bytes())
        for props in root.iter():
            if props.tag.endswith('}properties'):
                row={e.tag.split('}')[-1]:e.text for e in props}
                if row.get('BC_1MONTH'):rates.append(dict(rate_date=pd.Timestamp(row['NEW_DATE']),rate=np.log1p(float(row['BC_1MONTH'])/100)))
    rates=pd.DataFrame(rates).sort_values('rate_date').drop_duplicates('rate_date')
    # Use last available origin-date rate, never target-date rate.
    aligned=pd.merge_asof(d[['date']],rates,left_on='date',right_on='rate_date',direction='backward')
    assert aligned.rate.notna().all()
    returns=np.diff(np.log(d.close.to_numpy()));dt=d.date.diff().dt.total_seconds().to_numpy()[1:]/(365.25*86400)
    carry=aligned.rate.to_numpy()[:-1]
    return d,returns,dt,carry


def main():
    d,returns,dt,carry=load_training()
    source=ROOT/'data/processed/physical_measure/q_reference_20260902'
    out=ROOT/'outputs/physical_measure/20261006-fixed-q-candidates';out.mkdir(parents=True,exist_ok=True)
    for model in ['heston','bates','full_bates_hawkes']:
        q=json.loads((source/(model+'.json')).read_text())['parameters'];q=dict(q)
        q['xi']=q.get('xi',q.get('sigma'))
        branching=q.get('branching_ratio',0.)
        upperc=min(4.,.95/branching) if branching else 4.
        bounds=[(-15.,15.),(-2.,2.)]+([] if model=='heston' else [(np.log(.25),np.log(upperc)),(-3.,3.)])
        x0=np.array([2.,.7]+([] if model=='heston' else [0.,0.]))
        def expand(x):return np.r_[x,[0.,0.]] if model=='heston' else x
        evaluations=[0];start=time.time()
        def objective(x):
            evaluations[0]+=1
            try:v=physical_filter(returns,dt,carry,q,expand(x),particles=128,seed=704)
            except (ValueError,OverflowError):v=1e12
            if evaluations[0]%50==0:print(model,evaluations[0],round(v,2),'seconds',round(time.time()-start),flush=True)
            return v
        fit=minimize(objective,x0,method='Powell',bounds=bounds,options=dict(maxiter=10,maxfev=350,xtol=.015,ftol=1e-5))
        checks=[]
        for particles,seed in [(512,704),(1024,704),(1024,705),(1024,706)]:
            result=physical_filter(returns,dt,carry,q,expand(fit.x),particles=particles,seed=seed,return_diagnostics=True)
            result.pop('log_scores');checks.append(dict(particles=particles,seed=seed,**result))
        result=dict(status='EXPLORATORY_FIXED_Q_NOT_DCF_ADMITTED',model=model,underlying='GLD_USD_PER_SHARE',cutoff='2026-09-02',training_first=str(d.date.iloc[0].date()),observations=len(returns),q_parameters=q,
                    premia_names=['eta_price','log_kappa_p_over_q','log_intensity_ratio','mark_shift_in_sd'],premia=expand(fit.x).tolist(),negative_log_likelihood=float(fit.fun),optimizer_success=bool(fit.success),optimizer_message=str(fit.message),evaluations=evaluations[0],elapsed_seconds=time.time()-start,particle_checks=checks,
                    limitations=['Current Q coefficients imposed over historical training, not historical OOS.', 'Euler particle likelihood requires time-step and particle convergence.', 'Parameter uncertainty and identification not established.', 'One-month Treasury par yields are a short-rate proxy.', 'GLD-to-gold basis and corporate FCFF are not implemented by this fit.'])
        (out/(model+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print('FINISHED',model,fit.x,fit.fun,flush=True)
if __name__=='__main__':main()
