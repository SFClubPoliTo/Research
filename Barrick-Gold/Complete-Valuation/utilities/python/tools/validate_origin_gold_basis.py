"""Score completed GLD physical forecasts after origin-only gold conversion."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import pandas as pd

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
sys.path.insert(0,str(ROOT/'utilities/python'))
from barrick_unified.gold_basis import forecast_log_basis,gld_forecast_to_gold
from barrick_unified.physical_oos_summary import summarize_matched_origins


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--experiment',action='append',required=True)
    args=parser.parse_args()
    if Path(args.run_id).name!=args.run_id or args.run_id in ['.','..']:
        parser.error('run-id must be one directory name')
    output=ROOT/'outputs/physical_measure'/args.run_id
    if output.exists():
        parser.error('refusing to overwrite an experiment')
    basis_path=ROOT/'data/raw/ib_local/physical_history_20261005/gold_gld_synchronous_local.csv'
    basis=pd.read_csv(basis_path,parse_dates=['date'])
    if basis.date.duplicated().any():
        raise ValueError('duplicate synchronous basis date')
    experiments={};inputs=[];excluded=[];detail=[]
    for item in args.experiment:
        model,run=item.split('=',1)
        if Path(run).name!=run or run in ['.','..']:
            parser.error('input run must be one directory name')
        for source in sorted((ROOT/'outputs/physical_measure'/run).glob('*.json')):
            if source.name=='summary.json':continue
            payload=json.loads(source.read_text())
            rows=payload if isinstance(payload,list) else [payload]
            if not rows or any('target_date' not in row for row in rows):continue
            inputs.append(dict(path=source.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
            for row in rows:
                origin,target=pd.Timestamp(row['origin']),pd.Timestamp(row['target_date'])
                origin_row=basis[basis.date==origin];target_row=basis[basis.date==target]
                if origin_row.empty or target_row.empty:
                    excluded.append(dict(model=model,origin=row['origin'],target=row['target_date'],reason='MISSING_SYNCHRONOUS_DATE'))
                    continue
                fitted=forecast_log_basis(basis,origin,target)
                mean=row.get('predictive_mean',row.get('forecast_mean'))
                quantiles=row.get('predictive_quantiles',row.get('quantiles'))
                mean_gold,q_gold=gld_forecast_to_gold(mean,quantiles,fitted['log_ratio_prediction'])
                actual=float(target_row.gold_midpoint_usd_oz.iloc[0])
                transformed=dict(row,predictive_mean=mean_gold,predictive_quantiles=q_gold,
                                 target=actual,no_change_error=fitted['gold_origin']-actual,
                                 forecast_error=mean_gold-actual,training_last=fitted['training_last'])
                experiments.setdefault(model,[]).append(transformed)
                detail.append(dict(model=model,origin=row['origin'],target=row['target_date'],
                                   mean_gold_usd_oz=mean_gold,target_gold_usd_oz=actual,
                                   gold_quantiles=q_gold,basis=fitted))
    if set(experiments)!={item.split('=',1)[0] for item in args.experiment}:
        raise ValueError('requested model has no admissible converted observations')
    result=summarize_matched_origins(experiments)
    result.update(status='ORIGIN_PHYSICAL_GOLD_BASIS_DIAGNOSTIC_NOT_DCF_ADMITTED',
                  units='USD_PER_TROY_OUNCE',interpretation='Matched conditional physical gold predictions; deterministic estimated basis and plug-in parameters.',
                  excluded=excluded,inputs=inputs,basis_sha256=hashlib.sha256(basis_path.read_bytes()).hexdigest(),
                  limitations=['Basis and parameter uncertainty omitted.',
                               'Gold midpoint is not Barrick realized selling price.',
                               'No FCFF, capital structure or corporate valuation inferred.'])
    output.mkdir(parents=True)
    local=ROOT/'data/raw/ib_local'/args.run_id
    local.mkdir(exist_ok=False)
    (local/'converted_predictions.json').write_text(json.dumps(detail,indent=2)+'\n',encoding='utf-8')
    (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','common_pairs']},indent=2))


if __name__=='__main__':main()
