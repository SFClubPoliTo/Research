"""Refit fixed-Q physical premia at a declared particle/time resolution.

This is a current-date conditional estimation experiment. It does not use
current Q coefficients for historical OOS forecasts, and does not admit a DCF.
Independent seeds and a finer time grid assess the fitted likelihood.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.optimize import minimize

from fit_physical_candidates import ROOT, load_training, physical_filter
from barrick_unified.physical_measure import diffusion_novikov_horizon


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--models', nargs='+', choices=['heston', 'bates', 'full_bates_hawkes'],
                        default=['heston', 'bates', 'full_bates_hawkes'])
    parser.add_argument('--particles', type=int, default=512)
    parser.add_argument('--substeps', type=int, default=16)
    parser.add_argument('--max-evaluations', type=int, default=200)
    parser.add_argument('--training-seeds', nargs='+', type=int, default=[704, 705])
    args = parser.parse_args()
    if Path(args.run_id).name != args.run_id or args.run_id in ['.', '..']:
        parser.error('run-id must be a single directory name')
    if args.particles < 16 or args.substeps < 1 or args.max_evaluations < 1:
        parser.error('positive resolution and evaluation budget required')
    output = ROOT/'outputs/physical_measure'/args.run_id
    if output.exists():
        parser.error('refusing to overwrite an existing experiment')
    output.mkdir(parents=True)
    dates, returns, dt, carry = load_training()
    for model in args.models:
        source = ROOT/'outputs/physical_measure/20261006-fixed-q-candidates'/f'{model}.json'
        frozen = json.loads(source.read_text(encoding='utf-8'))
        q = frozen['q_parameters']
        active = 2 if model == 'heston' else 4
        branching = q.get('alpha', 0.)/q.get('beta', 1.)
        upper_c = min(4., .95/branching) if branching else 4.
        bounds = [(-15., 15.), (-2., 2.)]
        if active == 4:
            bounds += [(np.log(.25), np.log(upper_c)), (-3., 3.)]
        evaluations = 0
        started = time.monotonic()

        def expand(x):
            return np.r_[x, [0., 0.]] if active == 2 else x

        def objective(x):
            nonlocal evaluations
            evaluations += 1
            premia = expand(x)
            eta_variance = q['kappa']*(1-np.exp(premia[1]))/q['xi']
            horizon = diffusion_novikov_horizon(q['kappa'], q['xi'], q['rho'],
                                               premia[0], eta_variance)
            if horizon <= 5.:
                return 1e12
            try:
                values = [physical_filter(returns, dt, carry, q, premia,
                                          particles=args.particles, substeps=args.substeps,
                                          seed=seed) for seed in args.training_seeds]
                loss = float(np.mean(values))
            except (ValueError, OverflowError):
                loss = 1e12
            if evaluations % 10 == 0:
                print(model, 'evaluation', evaluations, 'mean NLL', round(loss, 3),
                      'seconds', round(time.monotonic()-started), flush=True)
            return loss

        initial = np.asarray(frozen['premia'][:active])
        initial_loss = objective(initial)
        fitted = minimize(objective, initial, method='Powell', bounds=bounds,
                          options={'maxfev': args.max_evaluations, 'maxiter': 20,
                                   'xtol': .01, 'ftol': 1e-6})
        selected = fitted.x if fitted.fun < initial_loss else initial
        checks = []
        for substeps in [args.substeps, 2*args.substeps]:
            for seed in [1704, 1705, 1706]:
                result = physical_filter(returns, dt, carry, q, expand(selected),
                                         particles=max(1024, args.particles), substeps=substeps,
                                         seed=seed, return_diagnostics=True)
                result.pop('log_scores')
                initial_nll = physical_filter(returns, dt, carry, q, expand(initial),
                                              particles=max(1024, args.particles),
                                              substeps=substeps, seed=seed)
                checks.append(dict(seed=seed, particles=max(1024, args.particles),
                                   initial_candidate_nll=initial_nll,
                                   refit_minus_initial_nll=result['negative_log_likelihood']-initial_nll,
                                   **result))
        payload = dict(status='CONDITIONAL_REFIT_NOT_DCF_ADMITTED', model=model,
                       cutoff=str(dates.date.iloc[-1].date()), observations=len(returns),
                       source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                       q_parameters=q, premia=expand(selected).tolist(),
                       initial_mean_nll=initial_loss, fitted_mean_nll=float(min(fitted.fun, initial_loss)),
                       optimizer_success=bool(fitted.success), optimizer_message=str(fitted.message),
                       evaluations=evaluations, training_particles=args.particles,
                       training_substeps=args.substeps, training_seeds=args.training_seeds,
                       independent_checks=checks, elapsed_seconds=time.monotonic()-started,
                       limitations=['Current Q coefficients held fixed over historical estimation.',
                                    'Not a joint option/return estimation or historical physical OOS.',
                                    'Jump-density admissibility and premium identification require separate evidence.',
                                    'No automatic convergence or corporate-valuation admission.'])
        (output/f'{model}.json').write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')
        print('FINISHED', model, 'optimizer success', bool(fitted.success), flush=True)


if __name__ == '__main__':
    main()
