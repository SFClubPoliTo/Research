"""Audit saved Q/P links, warm-start chronology and independent filter checks."""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    directory=ROOT/'outputs/physical_measure'
    source=directory/'20261011-four-model-complete/summary.json'
    summary=json.loads(source.read_text())
    q_by_hash={}
    for path in directory.glob('*origin-q-*/*.json'):
        payload=json.loads(path.read_text())
        if payload.get('status')=='DATED_Q_CALIBRATION_NOT_PHYSICAL_FORECAST':
            q_by_hash[digest(path)]=(path,payload)
    metrics={}; warm_links=0; q_links=0
    for item in summary['inputs']:
        path=ROOT/item['path']
        assert digest(path)==item['sha256'], path
        payload=json.loads(path.read_text())
        records=payload if isinstance(payload,list) else [payload]
        for row in records:
            if 'independent_checks' not in row:
                continue
            model=row.get('model','heston')
            stats=metrics.setdefault(model,dict(origins=0,optimizer_failures=[],
                recorded_warm_initializations=0,origins_all_independent_losses_improve=0,
                origins_mixed_or_no_improvement=0,within_grid_seed_nll_spreads=[]))
            stats['origins']+=1
            if not row.get('optimizer_success',row.get('p_optimizer_success',False)):
                stats['optimizer_failures'].append(row['origin'])
            assert row['origin'] < row['target_date']
            for artifact, artifact_path in [(row,path)]:
                if artifact.get('source_q_sha256'):
                    q_path,q=q_by_hash[artifact['source_q_sha256']]
                    assert q['origin']==row['origin'] and q['model']==model
                    q_links+=1
                    artifact_pairs=[(artifact,artifact_path),(q,q_path)]
                else:
                    artifact_pairs=[(artifact,artifact_path)]
                for record,record_path in artifact_pairs:
                    prior=record.get('initialization_source')
                    if prior:
                        prior_path=record_path.parent/prior['source_file']
                        assert digest(prior_path)==prior['source_sha256']
                        assert prior['origin'] < record['origin']
                        assert json.loads(prior_path.read_text())['origin']==prior['origin']
                        warm_links+=1
            stats['recorded_warm_initializations']+=int(bool(row.get('initialization_source')))
            checks=row['independent_checks']
            gains=[check['fitted_minus_zero_premium_nll'] for check in checks]
            all_improve=all(np.isfinite(gain) and gain<0 for gain in gains)
            stats['origins_all_independent_losses_improve']+=int(all_improve)
            stats['origins_mixed_or_no_improvement']+=int(not all_improve)
            for steps in sorted({check['substeps'] for check in checks}):
                values=[check['nll'] for check in checks if check['substeps']==steps]
                stats['within_grid_seed_nll_spreads'].append(float(max(values)-min(values)))
    for stats in metrics.values():
        spreads=stats.pop('within_grid_seed_nll_spreads')
        stats['within_grid_seed_nll_spread_median']=float(np.median(spreads))
        stats['within_grid_seed_nll_spread_max']=float(max(spreads))
    result=dict(status='SAVED_LINKS_AND_CHRONOLOGY_VERIFIED_NOT_CONVERGENCE_CERTIFICATE',
        summary_sha256=digest(source),source_code_sha256=digest(Path(__file__)),
        q_links_verified=q_links,warm_links_verified=warm_links,models=metrics,
        note='Seed spreads are numerical diagnostics, not confidence intervals or uncertainty propagation.')
    target=directory/'20261011-four-model-complete/numerical_audit.json'
    if target.exists(): raise FileExistsError(target)
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
