"""Targeted filter stress check at each jump family's largest saved seed spread.

Frozen premia are evaluated, not re-estimated; this is not new OOS evidence.
"""
import hashlib
import argparse
import json
from pathlib import Path
import time

import numpy as np
from fit_physical_candidates import ROOT, load_training, physical_filter


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--counts-only',action='store_true',help='Integrate Bates Poisson counts as well as marks')
    args=parser.parse_args()
    base=ROOT/'outputs/physical_measure'
    summary=json.loads((base/'20261011-four-model-complete/summary.json').read_text())
    output=base/('20261011-integrated-counts-stress' if args.counts_only else '20261011-integrated-marks-stress')
    output.mkdir(exist_ok=False)
    history,returns,dt,carry=load_training()
    for model in (['bates'] if args.counts_only else ['bates','full_bates_hawkes']):
        candidates=[]
        for item in summary['inputs']:
            path=ROOT/item['path']; row=json.loads(path.read_text())
            if not isinstance(row,dict) or row.get('model')!=model:continue
            checks=row['independent_checks']
            spread=max(np.ptp([c['nll'] for c in checks if c['substeps']==steps])
                       for steps in {c['substeps'] for c in checks})
            candidates.append((float(spread),path,row))
        old_spread,path,row=max(candidates,key=lambda item:item[0])
        count=row['training_returns'];q=row['q_parameters'];premia=row['premia']
        assert str(history.date.iloc[count].date())==row['origin']
        results=[];started=time.perf_counter()
        for old in row['independent_checks']:
            result=physical_filter(returns[:count],dt[:count],carry[:count],q,premia,
                particles=1024,seed=old['seed'],substeps=old['substeps'],
                integrate_marks=True,integrate_poisson_counts=args.counts_only,return_diagnostics=True)
            result.pop('log_scores')
            results.append(dict(seed=old['seed'],**result))
            print(model,row['origin'],old['substeps'],old['seed'],result['negative_log_likelihood'],flush=True)
        spans={str(steps):float(np.ptp([r['negative_log_likelihood'] for r in results if r['substeps']==steps]))
               for steps in {r['substeps'] for r in results}}
        payload=dict(status='TARGETED_NUMERICAL_STRESS_CHECK_NOT_REFIT_OR_OOS_VALIDATION',
            model=model,origin=row['origin'],selection='Largest saved within-grid seed NLL spread in the completed panel',
            poisson_counts_integrated=args.counts_only,
            source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            filter_sha256=hashlib.sha256((ROOT/'src/barrick_unified/physical_filter.py').read_bytes()).hexdigest(),
            original_max_within_grid_seed_spread=old_spread,
            integrated_within_grid_seed_spreads=spans,results=results,elapsed_seconds=time.perf_counter()-started)
        (output/f'{model}.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
        print('FINISHED',model,old_spread,spans,flush=True)


if __name__=='__main__':main()
