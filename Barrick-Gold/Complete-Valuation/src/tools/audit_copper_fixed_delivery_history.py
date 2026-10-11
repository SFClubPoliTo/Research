"""Audit fixed-delivery copper history before a same-underlying physical fit."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())


def main():
    raw=ROOT/'data/raw/ib_local/physical_history_20261005'
    source=raw/'hg_dec2026.csv'
    manifest=json.loads((raw/'manifest.json').read_text())
    request=next(r for r in manifest['requests'] if r['name']=='hg_dec2026')
    data=pd.read_csv(source,parse_dates=['date']).sort_values('date')
    if data.date.duplicated().any():raise ValueError('duplicate fixed-delivery date')
    excluded_future=int((data.date>pd.Timestamp('2026-09-02')).sum())
    data=data[data.date<='2026-09-02'].copy()
    eligible=(data.volume>=100)&(data.close>0)&np.isfinite(data.close)
    pairs=eligible.to_numpy()[:-1]&eligible.to_numpy()[1:]
    # Adjacency refers to the original observed date sequence, not the filtered
    # sequence. Illiquid gaps must not become artificial one-session returns.
    target_dates=data.date.to_numpy()[1:][pairs]
    origin_dates=data.date.to_numpy()[:-1][pairs]
    years=(target_dates-origin_dates)/np.timedelta64(1,'s')/(365.25*86400)
    longest=current=0
    for value in eligible:
        current=current+1 if value else 0
        longest=max(longest,current)
    output=ROOT/'outputs/physical_measure/20261008-copper-fixed-delivery-audit'
    if output.exists():raise ValueError('refusing to overwrite frozen audit')
    output.mkdir(parents=True)
    result=dict(status='FIXED_DELIVERY_HISTORY_AUDIT_NOT_P_FIT_OR_DCF',cutoff='2026-09-02',
          contract=request['contract']['localSymbol'],conId=request['contract']['conId'],
          expiry=request['contract']['lastTradeDateOrContractMonth'],
          original_rows=len(data)+excluded_future,rows_after_cutoff_excluded=excluded_future,
          historical_rows=len(data),zero_volume_rows=int((data.volume==0).sum()),
          minimum_volume=100,eligible_prices=int(eligible.sum()),
          eligible_adjacent_return_pairs=int(pairs.sum()),observed_pair_years=float(years.sum()),
          longest_eligible_observation_run=longest,
          first_eligible=str(data.loc[eligible,'date'].iloc[0].date()),
          last_eligible=str(data.loc[eligible,'date'].iloc[-1].date()),
          raw_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
          source_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          limitations=['Daily futures closes may be settlement prices, not synchronized option snapshot prices.',
            'Target liquidity filtering creates selected observed-return support; exclusions must be retained.',
            'Gaps require latent-state propagation rather than treating accepted pairs as consecutive observations.',
            'A fixed delivery expires in 2026 and does not identify a five-year spot or rolling-delivery law.',
            'Rotating delivery histories cannot be substituted silently for this contract.'])
    (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
