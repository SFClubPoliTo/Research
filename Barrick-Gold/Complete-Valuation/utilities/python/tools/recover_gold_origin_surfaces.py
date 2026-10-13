"""Recover historical observed GLD surfaces for new origin-only calibration.

Recovered row-level option inputs stay in the local licensed-data directory.
Only counts, dates and hashes are exported. Original model predictions are
discarded; no historical Q parameters are claimed to have been recovered.
"""
from pathlib import Path
import sys,json,hashlib
import pandas as pd

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
sys.path.insert(0,str(ROOT/'utilities/python'))
from barrick_unified.physical_origins import observed_origin_surface


def main():
    source=ROOT/'data/processed/audit_inputs/outputs/oos/rolling/option_forecasts.csv'
    observations=pd.read_csv(source)
    raw=ROOT/'data/raw/ib_local/gold_origin_surfaces_20261007'
    raw.mkdir(parents=True,exist_ok=True)
    prices=pd.read_csv(ROOT/'data/raw/ib_local/physical_history_20261005/gld_rth.csv')
    closes=dict(zip(prices.date,prices.close));rows=[]
    for date in sorted(observations.date.unique()):
        try:
            surface=observed_origin_surface(observations,date)
            origin_spot=float(surface.spot.iloc[0])
            difference=abs(origin_spot-float(closes[date]))
            if difference>1e-8:
                raise ValueError('option spot differs from dated GLD regular-session close')
            destination=raw/f'{date}.csv';surface.to_csv(destination,index=False)
            rows.append(dict(origin=date,status='OBSERVED_INPUTS_RECOVERED_Q_REFIT_REQUIRED',
                             points=len(surface),expiries=int(surface.expiry.nunique()),
                             spot_close_difference=difference,
                             sha256=hashlib.sha256(destination.read_bytes()).hexdigest()))
        except (ValueError,KeyError) as exc:
            rows.append(dict(origin=date,status='NOT_ADMITTED',reason=str(exc)))
    output=ROOT/'outputs/physical_measure/20261007-origin-surface-recovery'
    output.mkdir(exist_ok=True)
    result=dict(status='DATED_OBSERVED_INPUTS_NOT_HISTORICAL_Q_PARAMETERS',budget=64,
                source=source.relative_to(ROOT).as_posix(),
                source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                discarded=['prior-origin model predictions','benchmark predictions','support flags'],
                provider_measure='Preserved legacy observed price and IV fields; not asserted transaction prices.',
                private_output='data/raw/ib_local/gold_origin_surfaces_20261007',origins=rows)
    (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(admitted=sum(row['status'].startswith('OBSERVED') for row in rows),
                          excluded=sum(row['status']=='NOT_ADMITTED' for row in rows),
                          origins=len(rows))))


if __name__=='__main__':main()
