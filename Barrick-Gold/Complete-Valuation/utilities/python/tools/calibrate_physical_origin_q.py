"""Origin-specific pricing fits for subsequent physical-premium estimation.

Only the dated observed surface enters. Nested candidates come from the same
origin, never from a later-date fit. No physical forecast is produced here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
sys.path.insert(0, str(ROOT/'utilities/python/pricing'))
from Heston import Heston
from Bates import Bates
from Hawkes import ExactHawkesCalibration
from dated_initialization import previous_fit, parameter_vector


def calibrate_origin(frame, model, *, seed=104, previous=None):
    spot = float(frame.spot.iloc[0])
    prior = previous['parameters'] if previous else None
    heston_guess = (previous.get('nested_heston_parameters', prior) if previous else None)
    heston = Heston.calibrate_heston(frame, spot, seed=seed, return_report=True,
        initial_guess=parameter_vector(heston_guess, 'heston') if heston_guess else None)
    if not Heston._admissible(heston.x) or heston.objective >= Heston.INVALID_OBJECTIVE:
        raise ValueError('inadmissible Heston origin fit')
    if model == 'heston':
        result = heston.as_dict()
        result['parameters']['xi'] = result['parameters']['sigma']
        return result
    bates_guess = (prior if model == 'bates' else previous.get('nested_bates_parameters')) if previous else None
    bates = Bates.calibrate_bates(frame, spot, seed=seed, heston_seed=heston.x, return_report=True,
        initial_guess=parameter_vector(bates_guess, 'bates') if bates_guess else None)
    if bates.objective >= Bates.INVALID_OBJECTIVE:
        raise ValueError('inadmissible Bates origin fit')
    if model == 'bates':
        result = bates.as_dict()
        result['parameters']['xi'] = result['parameters']['sigma']
        result['nested_heston_parameters'] = heston.params
        return result
    started = time.monotonic()
    hawkes_guess = parameter_vector(prior, model) if prior else None
    hawkes = ExactHawkesCalibration.calibrate_heston(frame, spot, bates_seed=bates.x, seed=seed,
                                                    hawkes_seed=hawkes_guess,
                                                    global_cos_N=256, local_cos_N=256)
    if hawkes_guess is not None and (not hawkes.success or not np.isfinite(hawkes.fun) or hawkes.fun >= 1e8):
        hawkes = ExactHawkesCalibration.calibrate_heston(frame, spot, bates_seed=bates.x,
            seed=seed, global_cos_N=256, local_cos_N=256)
    q = ExactHawkesCalibration.unpack_heston_params(hawkes.x)
    if not np.isfinite(hawkes.fun) or hawkes.fun >= 1e8:
        raise ValueError('inadmissible Hawkes origin fit')
    return dict(parameters=q, objective=float(hawkes.fun), success=bool(hawkes.success),
                message=str(hawkes.message), elapsed_seconds=time.monotonic()-started,
                nested_bates_objective=bates.objective,
                nested_heston_objective=heston.objective,
                nested_heston_parameters=heston.params, nested_bates_parameters=bates.params,
                warm_start_used=bool(hawkes.get('warm_start_used', False)),
                global_search_used=bool(hawkes.get('global_search_used', True)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--origins', nargs='+', required=True)
    parser.add_argument('--model', choices=['heston','bates','full_bates_hawkes'], required=True)
    parser.add_argument('--resume', action='store_true', help='Validate and retain completed dated fits')
    parser.add_argument('--cold-start', action='store_true', help='Disable previous-origin initialization')
    args = parser.parse_args()
    if Path(args.run_id).name != args.run_id or args.run_id in ['.', '..']:
        parser.error('run-id must be a directory name')
    output = ROOT/'outputs/physical_measure'/args.run_id
    if output.exists() and not args.resume:
        parser.error('refusing to overwrite an experiment')
    sources = ROOT/'data/raw/ib_local/gold_origin_surfaces_20261007'
    origins = sorted(set(pd.Timestamp(s).strftime('%Y-%m-%d') for s in args.origins))
    frames = {}
    for origin in origins:
        path = sources/f'{origin}.csv'
        frame = pd.read_csv(path)
        if not (pd.to_datetime(frame.date) == origin).all() or (pd.to_datetime(frame.curve_date) > origin).any():
            raise ValueError('surface/curve date violates origin')
        if len(frame) != 64 or frame.expiry.nunique() < 3 or frame.spot.nunique() != 1:
            raise ValueError('origin surface contract not satisfied')
        frames[origin] = frame
    output.mkdir(parents=True, exist_ok=args.resume)
    source_code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for origin, frame in frames.items():
        destination = output/f'{origin}.json'
        if destination.exists():
            saved = json.loads(destination.read_text(encoding='utf-8'))
            current_hash = hashlib.sha256((sources/f'{origin}.csv').read_bytes()).hexdigest()
            if (saved.get('origin') != origin or saved.get('model') != args.model
                    or saved.get('source_sha256') != current_hash
                    or saved.get('status') != 'DATED_Q_CALIBRATION_NOT_PHYSICAL_FORECAST'
                    or not saved.get('parameters')):
                raise ValueError(f'incompatible completed calibration: {origin}')
            print('RETAINED', args.model, origin, flush=True)
            continue
        print('CALIBRATING', args.model, origin, flush=True)
        previous, initial_source = (None, None) if args.cold_start else previous_fit(output, origin, args.model)
        result = calibrate_origin(frame, args.model, previous=previous)
        result.update(origin=origin, model=args.model, measure='Q', contracts=len(frame),
                      source_sha256=hashlib.sha256((sources/f'{origin}.csv').read_bytes()).hexdigest(),
                      source_code_sha256=source_code_hash,
                      pricing_code_sha256={name:hashlib.sha256((ROOT/'utilities/python/pricing'/name).read_bytes()).hexdigest()
                          for name in ['Heston.py','Bates.py','Hawkes.py','calibration_core.py','dated_initialization.py']},
                      status='DATED_Q_CALIBRATION_NOT_PHYSICAL_FORECAST',
                      initialization='Previous successful origin with local refinement and global fallback' if previous else 'Generic population and same-origin nested candidates only',
                      initialization_source=initial_source)
        temporary = destination.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        temporary.replace(destination)
        print('FINISHED', origin, result['success'], result['objective'], flush=True)


if __name__ == '__main__':
    main()
