"""Training-only physical GBM and GLD/gold basis forecasts.

Historical diffusion estimates are a P-only benchmark, not a joint calibration
to historical option surfaces. Quarterly forecasts overlap: counts are not
independent repetitions. No current Q parameter enters an earlier forecast.
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
from scipy.stats import norm
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file());sys.path.insert(0,str(ROOT/'utilities/python'))
from barrick_unified.physical_gbm import fit_gbm


def main():
    raw=ROOT/'data/raw/ib_local/physical_history_20261005'
    path=raw/'gold_gld_synchronous_local.csv';basis=pd.read_csv(path,parse_dates=['date'])
    gld=pd.read_csv(raw/'gld_rth.csv',parse_dates=['date']);gld=gld[gld.date<='2026-09-02'].sort_values('date')
    rows=[]
    for i in range(252,len(basis)-1):
        origin=basis.iloc[i];training=basis.iloc[:i+1]
        history=gld[gld.date<=origin.date]
        r=np.diff(np.log(history.close));dt=np.diff(history.date.to_numpy())/np.timedelta64(1,'s')/(365.25*86400)
        fit=fit_gbm(r,dt)
        time=(training.date-training.date.iloc[0]).dt.total_seconds().to_numpy()/(365.25*86400)
        b,a=np.polyfit(time,training.log_share_to_ounce_ratio,1)
        gold_r=np.diff(np.log(training.gold_midpoint_usd_oz));gold_dt=np.diff(training.date.to_numpy())/np.timedelta64(1,'s')/(365.25*86400)
        gold_fit=fit_gbm(gold_r,gold_dt)
        for horizon in ['next_session','90_calendar_days']:
            j=i+1 if horizon=='next_session' else int(basis.date.searchsorted(origin.date+pd.Timedelta(days=90)))
            if j>=len(basis):continue
            target=basis.iloc[j];h=(target.date-origin.date).total_seconds()/(365.25*86400)
            ratio_prediction=a+b*(time[-1]+h)
            log_prediction=np.log(origin.gld_usd_share)+(fit.arithmetic_drift-.5*fit.sigma**2)*h-ratio_prediction
            models=[('gld_gbm_trend_basis',log_prediction,fit.sigma),
                    ('direct_gold_gbm',np.log(origin.gold_midpoint_usd_oz)+(gold_fit.arithmetic_drift-.5*gold_fit.sigma**2)*h,gold_fit.sigma),
                    ('gold_no_change_mean',np.log(origin.gold_midpoint_usd_oz)-.5*gold_fit.sigma**2*h,gold_fit.sigma)]
            actual=float(target.gold_midpoint_usd_oz)
            for model,mean,sigma in models:
                sd=sigma*np.sqrt(h);prediction=np.exp(mean+.5*sd*sd)
                pit=norm.cdf((np.log(actual)-mean)/sd)
                # Density is scored on USD/oz, including the log Jacobian.
                score=norm.logpdf(np.log(actual),loc=mean,scale=sd)-np.log(actual)
                rows.append(dict(origin=str(origin.date.date()),target=str(target.date.date()),horizon=horizon,model=model,
                    squared_error=(prediction-actual)**2,absolute_error=abs(prediction-actual),log_score=score,
                    covered_80=.1<=pit<=.9,covered_95=.025<=pit<=.975,pit=pit))
    predictions=pd.DataFrame(rows);predictions.to_csv(raw/'gold_physical_baseline_oos_local.csv',index=False)
    summaries=[]
    for (horizon,model),group in predictions.groupby(['horizon','model']):
        summaries.append(dict(horizon=horizon,model=model,n=len(group),rmse_usd_oz=float(np.sqrt(group.squared_error.mean())),
            mae_usd_oz=float(group.absolute_error.mean()),mean_log_density_usd_oz=float(group.log_score.mean()),
            coverage_80=float(group.covered_80.mean()),coverage_95=float(group.covered_95.mean())))
    out=ROOT/'outputs/physical_measure/20261006-gold-physical-baseline';out.mkdir(parents=True,exist_ok=True)
    result=dict(status='HISTORICAL_P_BASELINE_NOT_JOINT_P_Q_OR_DCF',cutoff='2026-09-02',minimum_basis_training_prices=253,
        summaries=summaries,input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        limitations=['P-only historical GBM diffusion: no historical option calibration used or validated by this run.',
                     'Basis trend is estimated at each origin and treated as deterministic in forecast distributions.',
                     'Parameter uncertainty is omitted from plug-in forecast intervals.',
                     'Quarterly targets use the first observed session at or after 90 calendar days; forecasts overlap.',
                     'Physical spot forecasts do not reconcile Barrick realized selling price, operations, FCFF or equity claims.'])
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(summaries,indent=2))


if __name__=='__main__':main()
