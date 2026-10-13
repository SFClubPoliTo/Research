"""Build a local-only, explicit-delivery copper return diagnostic."""
from pathlib import Path
import sys,json,hashlib
import pandas as pd
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file());sys.path.insert(0,str(ROOT/'utilities/python'))
from barrick_unified.futures_history import origin_selected_returns


def main():
    raw=ROOT/'data/raw/ib_local/physical_history_20261005/copper_strip'
    manifest=json.loads((raw/'manifest.json').read_text());frames=[];hashes=[]
    for request in manifest['requests']:
        if request['status']!='ACQUIRED':continue
        path=raw/(request['month']+'.csv');data=pd.read_csv(path)
        data['contract']=request['contract']['localSymbol']
        data['expiry']=pd.to_datetime(request['contract']['lastTradeDateOrContractMonth'],format='%Y%m%d')
        data['date']=pd.to_datetime(data.date);frames.append(data[data.date<='2026-09-02'])
        hashes.append(dict(file=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    panel=pd.concat(frames,ignore_index=True)
    returns=origin_selected_returns(panel);returns.to_csv(raw/'origin_selected_returns_local.csv',index=False)
    admitted=returns[returns.status=='ACCEPTED'].copy()
    out=ROOT/'outputs/physical_measure/20261006-copper-history';out.mkdir(parents=True,exist_ok=True)
    result=dict(status='ROTATING_FUTURES_DIAGNOSTIC_NOT_SPOT_OR_DCF',cutoff='2026-09-02',
        rule=dict(minimum_volume=100,minimum_days_to_expiry=30,selection='nearest eligible delivery at origin; target failures excluded without reselection'),
        status_counts=returns.status.value_counts().to_dict(),first_origin=str(admitted.origin.min().date()),last_target=str(admitted.target.max().date()),
        contracts=admitted.contract.value_counts().to_dict(),observed_years=float(admitted.dt_years.sum()),
        unavailable_requested_deliveries=[r['month'] for r in manifest['requests'] if r['status']!='ACQUIRED'],inputs=hashes,
        limitations=['Available delivery universe begins September 2025: not a historical front-month reconstruction.',
                     'Origin and target liquidity filters can select the estimation sample; report exclusions.',
                     'Rotating futures returns do not identify spot drift, convenience yield, or the five-year realized sales-price curve.',
                     'Daily futures close may be a settlement; same-clock spot basis remains unresolved.',
                     'The approximately 100-point option-surface budget is separate from daily underlying estimation history.'])
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','limitations']},indent=2))


if __name__=='__main__':main()
