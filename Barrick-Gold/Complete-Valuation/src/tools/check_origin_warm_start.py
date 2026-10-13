"""Check all three warm Q fits against frozen same-surface cold objectives.

Timing is the new total elapsed time, not a controlled cross-run speedup.
The frozen results are retained and this diagnostic does not admit a DCF.
"""
import hashlib
import json
from pathlib import Path
import time

import pandas as pd
from calibrate_physical_origin_q import ROOT, calibrate_origin


def main():
    output = ROOT/'outputs/physical_measure/20261009-warm-start-check'
    output.mkdir(exist_ok=False)
    source = ROOT/'data/raw/ib_local/gold_origin_surfaces_20261007/2026-07-14.csv'
    frame = pd.read_csv(source)
    runs = dict(heston='20261007-heston-origin-panel',bates='20261008-bates-origin-q-panel',
                full_bates_hawkes='20261008-full_bates_hawkes-origin-q-panel')
    for model, run in runs.items():
        base = ROOT/'outputs/physical_measure'/run
        prior_path, cold_path = base/'2026-07-13.json', base/'2026-07-14.json'
        prior, cold = [json.loads(p.read_text(encoding='utf-8')) for p in [prior_path,cold_path]]
        assert prior['origin'] < cold['origin'] == '2026-07-14'
        assert cold['source_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
        if model=='heston':
            prior = dict(parameters=prior['q_fit']['parameters'])
            cold = cold['q_fit']
        print('CHECKING',model,flush=True)
        started=time.perf_counter()
        result=calibrate_origin(frame,model,previous=prior)
        result.update(total_elapsed_seconds=time.perf_counter()-started,
            origin='2026-07-14',initialization_origin='2026-07-13',
            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            prior_sha256=hashlib.sha256(prior_path.read_bytes()).hexdigest(),
            cold_result_sha256=hashlib.sha256(cold_path.read_bytes()).hexdigest(),
            frozen_cold_objective=cold['objective'],
            status='WARM_START_NUMERICAL_CHECK_NOT_MODEL_SELECTION')
        (output/f'{model}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(model,result['total_elapsed_seconds'],result['objective'],cold['objective'],flush=True)


if __name__=='__main__':
    main()
