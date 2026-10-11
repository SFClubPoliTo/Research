"""Align licensed GLD trades and gold midpoint bars at actual exchange closes.

Writes observations only beneath the local licensed-data tree. Public output
contains aggregate diagnostics and hashes, never the underlying price series.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())


def main():
    raw=ROOT/'data/raw/ib_local/physical_history_20261005'
    paths=[raw/'gld_schedule.json',raw/'gld_rth.csv',*sorted((raw/'gold_hourly_chunks').glob('*.csv'))]
    schedule=json.loads(paths[0].read_text())
    sessions=[]
    for block in schedule['schedules']:
        for s in block['sessions']:
            end=pd.Timestamp(pd.to_datetime(s['endDateTime'],format='%Y%m%d-%H:%M:%S')).tz_localize(block['timeZone']).tz_convert('UTC')
            sessions.append(dict(date=pd.Timestamp(s['refDate']),end=end))
    sessions=pd.DataFrame(sessions).drop_duplicates()
    if sessions.date.duplicated().any():raise ValueError('conflicting schedules')
    gld=pd.read_csv(paths[1],parse_dates=['date'])[['date','close']].rename(columns={'close':'gld_usd_share'})
    gld=gld[gld.date<='2026-09-02']
    hourly=pd.concat([pd.read_csv(p) for p in paths[2:]],ignore_index=True)
    hourly['end']=pd.to_datetime(hourly.date,utc=True)+pd.Timedelta(hours=1)
    # Historical overlap must agree; no arbitrary keep-last correction.
    if (hourly.groupby('end').close.nunique()>1).any():raise ValueError('conflicting hourly observations')
    hourly=hourly.drop_duplicates('end')[['end','close']].rename(columns={'close':'gold_midpoint_usd_oz'})
    aligned=gld.merge(sessions,on='date',how='left',validate='one_to_one').merge(hourly,on='end',how='left',validate='many_to_one')
    missing=aligned[aligned.gold_midpoint_usd_oz.isna()]
    aligned=aligned.dropna().sort_values('date')
    aligned['log_share_to_ounce_ratio']=np.log(aligned.gld_usd_share/aligned.gold_midpoint_usd_oz)
    aligned.to_csv(raw/'gold_gld_synchronous_local.csv',index=False)
    t=(aligned.date-aligned.date.iloc[0]).dt.total_seconds().to_numpy()/(365.25*86400)
    y=aligned.log_share_to_ounce_ratio.to_numpy()
    slope,intercept=np.polyfit(t,y,1);residual=y-(intercept+slope*t)
    # Expanding-origin ratio forecast. Conversion error is measured against
    # next-date spot using observed next-date GLD; this is a basis-only test,
    # not a commodity-price forecast or end-to-end OOS valuation.
    errors=[];constant=[]
    for j in range(252,len(y)):
        b,a=np.polyfit(t[:j],y[:j],1)
        errors.append(np.expm1(y[j]-(a+b*t[j])))
        constant.append(np.expm1(y[j]-y[j-1]))
    out=ROOT/'outputs/physical_measure/20261006-gold-basis';out.mkdir(parents=True,exist_ok=True)
    result=dict(status='BASIS_DIAGNOSTIC_NOT_DCF_ADMITTED',cutoff='2026-09-02',aligned_prices=len(aligned),first=str(aligned.date.iloc[0].date()),last=str(aligned.date.iloc[-1].date()),
        missing_gld_dates=len(missing),early_close_observations=int((aligned.end.dt.tz_convert('US/Eastern').dt.hour<16).sum()),
        log_ratio_annual_trend=float(slope),log_ratio_residual_sd=float(residual.std(ddof=2)),basis_oos_count=len(errors),
        basis_trend_relative_rmse=float(np.sqrt(np.mean(np.square(errors)))),basis_previous_ratio_relative_rmse=float(np.sqrt(np.mean(np.square(constant)))),
        inputs=[dict(file=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths],
        limitations=['Hourly bar timestamps are starts; close is matched to the reported exchange-session end.',
                     'GLD trade close versus gold midpoint: quote/trade and venue basis remains.',
                     'Trend estimated empirically, not identified as management fee or structural long-run law.',
                     'Basis-only OOS conditions on target GLD; it does not establish commodity forecast accuracy.',
                     'Missing hourly history excluded, not filled; physical parameter and basis uncertainty remain.'])
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','limitations']},indent=2))


if __name__=='__main__':main()
