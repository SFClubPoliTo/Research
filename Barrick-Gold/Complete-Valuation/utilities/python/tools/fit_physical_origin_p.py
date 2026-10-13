"""Physical premium fit and next-session prediction from a dated Q artifact."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from fit_physical_candidates import ROOT, load_training, physical_filter
sys.path.insert(0, str(ROOT/'utilities/python/pricing'))
from dated_initialization import previous_fit
from barrick_unified.physical_paths import simulate_physical_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--q-run-id', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--particles', type=int, default=512)
    parser.add_argument('--substeps', type=int, default=16)
    parser.add_argument('--max-evaluations', type=int, default=240)
    parser.add_argument('--resume', action='store_true', help='Validate and retain completed forecasts')
    parser.add_argument('--cold-start', action='store_true', help='Disable previous-origin premium guess')
    args = parser.parse_args()
    for name in [args.run_id, args.q_run_id]:
        if Path(name).name != name or name in ['.', '..']:
            parser.error('run IDs must be directory names')
    sources = sorted((ROOT/'outputs/physical_measure'/args.q_run_id).glob('*.json'))
    if not sources:
        parser.error('no dated Q results')
    output = ROOT/'outputs/physical_measure'/args.run_id
    if output.exists() and not args.resume:
        parser.error('refusing to overwrite an experiment')
    output.mkdir(parents=True, exist_ok=args.resume)
    history, returns, dt, carry = load_training()
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for source in sources:
        calibration = json.loads(source.read_text())
        if calibration.get('status') != 'DATED_Q_CALIBRATION_NOT_PHYSICAL_FORECAST':
            raise ValueError('requires a dated pricing calibration artifact')
        destination = output/source.name
        if destination.exists():
            saved = json.loads(destination.read_text(encoding='utf-8'))
            if (saved.get('source_q_sha256') != hashlib.sha256(source.read_bytes()).hexdigest()
                    or saved.get('origin') != calibration['origin']
                    or saved.get('model') != calibration['model']
                    or saved.get('training_particles') != args.particles
                    or saved.get('training_substeps') != args.substeps
                    or saved.get('status') != 'CONDITIONAL_TWO_STAGE_OOS_NOT_DCF_ADMITTED'):
                raise ValueError(f'incompatible completed physical forecast: {source.name}')
            print('RETAINED', calibration['model'], calibration['origin'], flush=True)
            continue
        origin = pd.Timestamp(calibration['origin'])
        model = calibration['model']
        if model not in ['heston','bates','full_bates_hawkes']:
            raise ValueError('unsupported physical family')
        indices = np.flatnonzero((history.date == origin).to_numpy())
        if len(indices) != 1:
            raise ValueError('missing unique training endpoint')
        index = int(indices[0])
        if index+1 >= len(history):
            continue
        q = calibration['parameters']
        training = (returns[:index], dt[:index], carry[:index])
        # With zero jump support no jump premium is identifiable or activated.
        jumps = q.get('lambda0', q.get('lambd',0)) > 0 or q.get('lambda_bar',0) > 0
        active = 4 if model != 'heston' and jumps else 2
        branching = q.get('alpha',0)/q.get('beta',1)
        bounds = [(-15.,15.),(-2.,2.)]
        if active == 4:
            bounds += [(np.log(.25), np.log(min(4.,.95/branching) if branching else 4.)),(-3.,3.)]
        calls = 0

        def expand(x):
            return np.r_[x,0.,0.] if active == 2 else x

        def objective(x):
            nonlocal calls
            calls += 1
            loss = np.mean([physical_filter(*training,q,expand(x),particles=args.particles,
                                            substeps=args.substeps,seed=seed) for seed in [704,705]])
            if calls % 20 == 0:
                print(model, calibration['origin'], 'P evaluation', calls, flush=True)
            return float(loss)

        initial = np.zeros(active)
        initial_loss = objective(initial)
        previous, initial_source = (None, None) if args.cold_start else previous_fit(
            output, calibration['origin'], model, physical=True)
        start = initial.copy()
        start_loss = initial_loss
        if previous is not None:
            candidate = np.asarray(previous['premia'][:active], dtype=float)
            if candidate.shape == (active,) and np.isfinite(candidate).all():
                candidate = np.clip(candidate, np.asarray(bounds)[:,0], np.asarray(bounds)[:,1])
                candidate_loss = objective(candidate)
                if np.isfinite(candidate_loss) and candidate_loss < initial_loss:
                    start, start_loss = candidate, candidate_loss
        fit = minimize(objective,start,method='Powell',bounds=bounds,
                       options={'maxfev':args.max_evaluations,'xtol':.01,'ftol':1e-6})
        selected = fit.x if np.isfinite(fit.fun) and fit.fun < start_loss else start
        checks = []
        for substeps in [args.substeps,2*args.substeps]:
            for seed in [1704,1705,1706]:
                nll = physical_filter(*training,q,expand(selected),particles=1024,substeps=substeps,seed=seed)
                null = physical_filter(*training,q,expand(initial),particles=1024,substeps=substeps,seed=seed)
                checks.append(dict(seed=seed,substeps=substeps,nll=nll,fitted_minus_zero_premium_nll=nll-null))
        spot = float(history.close.iloc[index])
        paths = simulate_physical_paths(model,q,expand(selected),initial_price=spot,
                    output_times=[float(dt[index])],underlying_kind='spot_or_etf',
                    n_paths=65536,steps_per_year=365*32,carry_q=float(carry[index]),seed=2104)
        predictions = paths.price_endpoints[:,-1]
        target = float(history.close.iloc[index+1])
        quantiles = np.quantile(predictions,[.025,.1,.5,.9,.975])
        result = dict(status='CONDITIONAL_TWO_STAGE_OOS_NOT_DCF_ADMITTED',model=model,
                      origin=calibration['origin'],target_date=str(history.date.iloc[index+1].date()),
                      training_returns=index,source_q_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                      source_code_sha256=source_hash,q_parameters=q,premia=expand(selected).tolist(),
                      initialization_source=initial_source, initial_premia=expand(start).tolist(),
                      initialization='Previous successful origin if better than zero on current training likelihood',
                      active_premia=active,optimizer_success=bool(fit.success),optimizer_message=str(fit.message),
                      evaluations=calls,training_particles=args.particles,training_substeps=args.substeps,
                      independent_checks=checks,predictive_mean=float(predictions.mean()),
                      predictive_mean_mc_se=float(predictions.std(ddof=1)/np.sqrt(len(predictions))),
                      predictive_quantiles=quantiles.tolist(),target=target,
                      forecast_error=float(predictions.mean()-target),no_change_error=spot-target,
                      path_diagnostics=paths.diagnostics,
                      limitations=['Conditional structural Q coefficients over the historical P training sample.',
                                   'Parameter and option-state uncertainty not propagated.',
                                   'A successful optimizer is not an identification or convergence certificate.',
                                   'GLD forecast precedes gold basis, sales, FCFF and corporate valuation.'])
        temporary = destination.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        temporary.replace(destination)
        print('FINISHED',model,calibration['origin'],bool(fit.success),flush=True)


if __name__ == '__main__':
    main()
