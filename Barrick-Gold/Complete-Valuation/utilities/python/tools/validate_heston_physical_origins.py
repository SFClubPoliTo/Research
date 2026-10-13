"""Dated two-stage Heston experiment; Q options and P returns precede targets.

This conditional estimator is not joint maximum likelihood. It does not
propagate parameter uncertainty or admit corporate cash flows.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from fit_physical_candidates import ROOT, load_training, physical_filter
sys.path.insert(0, str(ROOT/'utilities/python/pricing'))
from Heston import Heston
from barrick_unified.physical_paths import simulate_physical_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--origins', nargs='+', required=True)
    parser.add_argument('--particles', type=int, default=512)
    parser.add_argument('--substeps', type=int, default=16)
    parser.add_argument('--max-evaluations', type=int, default=160)
    args = parser.parse_args()
    if Path(args.run_id).name != args.run_id or args.run_id in ['.', '..']:
        parser.error('run-id must be a directory name')
    output = ROOT/'outputs/physical_measure'/args.run_id
    if output.exists():
        parser.error('refusing to overwrite an experiment')
    # Validate every date before creating any output or starting a calibration.
    origins = sorted(set(pd.Timestamp(s).strftime('%Y-%m-%d') for s in args.origins))
    surfaces = ROOT/'data/raw/ib_local/gold_origin_surfaces_20261007'
    for origin in origins:
        if not (surfaces/f'{origin}.csv').is_file():
            parser.error(f'no observed surface for {origin}')
    output.mkdir(parents=True)
    history, returns, dt, carry = load_training()
    records = []
    previous_q = None
    for origin in origins:
        timestamp = pd.Timestamp(origin)
        source = surfaces/f'{origin}.csv'
        frame = pd.read_csv(source)
        if not (pd.to_datetime(frame.date) == timestamp).all():
            raise ValueError('surface date mismatch')
        if (pd.to_datetime(frame.curve_date) > timestamp).any():
            raise ValueError('future curve in origin surface')
        position = np.flatnonzero((history.date == timestamp).to_numpy())
        if len(position) != 1:
            raise ValueError('origin absent or duplicated in RTH history')
        index = int(position[0])
        if index+1 >= len(history):
            print('NO TARGET WITHIN FREEZE', origin, flush=True)
            continue
        spot = float(frame.spot.iloc[0])
        if not np.isclose(spot, float(history.close.iloc[index]), atol=1e-8, rtol=0):
            raise ValueError('origin option/return price mismatch')
        print('CALIBRATING Q', origin, flush=True)
        # Origins are sorted: the guess contains only an earlier fitted surface.
        report = Heston.calibrate_heston(frame, spot, seed=104, return_report=True,
                                         initial_guess=previous_q)
        if report.success:
            previous_q = report.x.copy()
        q = dict(report.params)
        q['xi'] = q['sigma']
        if not Heston._admissible(report.x) or report.objective >= Heston.INVALID_OBJECTIVE:
            raise ValueError('inadmissible origin Q calibration')
        training = (returns[:index], dt[:index], carry[:index])
        calls = 0

        def expand(x):
            return np.r_[x, 0., 0.]

        def objective(x):
            nonlocal calls
            calls += 1
            values = [physical_filter(*training, q, expand(x), particles=args.particles,
                                      substeps=args.substeps, seed=seed)
                      for seed in [704, 705]]
            if calls % 20 == 0:
                print(origin, 'P evaluation', calls, flush=True)
            return float(np.mean(values))

        # Zero premium is a dated, future-independent starting point.
        initial = np.zeros(2)
        initial_loss = objective(initial)
        fit = minimize(objective, initial, method='Powell', bounds=[(-15., 15.), (-2., 2.)],
                       options={'maxfev': args.max_evaluations, 'xtol': .01, 'ftol': 1e-6})
        selected = fit.x if fit.fun < initial_loss else initial
        checks = []
        for steps in [args.substeps, 2*args.substeps]:
            for seed in [1704, 1705, 1706]:
                nll = physical_filter(*training, q, expand(selected), particles=1024,
                                      substeps=steps, seed=seed)
                null = physical_filter(*training, q, expand(initial), particles=1024,
                                       substeps=steps, seed=seed)
                checks.append(dict(substeps=steps, seed=seed, nll=nll,
                                   fitted_minus_zero_premium_nll=nll-null))
        # Target price is first accessed below, after parameter estimation.
        horizon = float(dt[index])
        path = simulate_physical_paths('heston', q, expand(selected), initial_price=spot,
                    output_times=[horizon], underlying_kind='spot_or_etf',
                    n_paths=65536, steps_per_year=365*32, carry_q=float(carry[index]), seed=2104)
        forecast = path.price_endpoints[:, -1]
        target = float(history.close.iloc[index+1])
        quantiles = np.quantile(forecast, [.025, .1, .5, .9, .975])
        row = dict(origin=origin, target_date=str(history.date.iloc[index+1].date()),
                   status='CONDITIONAL_TWO_STAGE_OOS_NOT_DCF_ADMITTED',
                   training_returns=index, training_last=origin, surface_rows=len(frame),
                   source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   q_fit=report.as_dict(), premia=expand(selected).tolist(),
                   p_optimizer_success=bool(fit.success), p_optimizer_message=str(fit.message),
                   p_evaluations=calls, p_particles=args.particles, p_substeps=args.substeps,
                   independent_checks=checks, predictive_mean=float(forecast.mean()),
                   predictive_mean_mc_se=float(forecast.std(ddof=1)/np.sqrt(len(forecast))),
                   predictive_quantiles=quantiles.tolist(), target=target,
                   forecast_error=float(forecast.mean()-target), no_change_error=spot-target,
                   coverage95=bool(quantiles[0] <= target <= quantiles[-1]),
                   path_diagnostics=path.diagnostics)
        (output/f'{origin}.json').write_text(json.dumps(row, indent=2)+'\n', encoding='utf-8')
        records.append(row)
        print('FINISHED', origin, 'Q/P optimizer', report.success, fit.success, flush=True)
    summary = dict(status='CONDITIONAL_TWO_STAGE_OOS_NOT_DCF_ADMITTED',
                   origins_requested=origins, targets=len(records),
                   source_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   rmse=float(np.sqrt(np.mean([r['forecast_error']**2 for r in records]))) if records else None,
                   no_change_rmse=float(np.sqrt(np.mean([r['no_change_error']**2 for r in records]))) if records else None,
                   limitations=['Conditional two-stage estimation, not joint maximum likelihood.',
                     'Options condition the initial forecast variance; historical filter starts at theta_P.',
                     'Constant structural Q coefficients imposed over each origin training history.',
                     'Parameter and option-state estimation uncertainty are not propagated.',
                     'Single forecast simulation resolution; independent likelihood refinement reported.',
                     'GLD USD/share forecasts, not physical gold selling prices or FCFF.',
                     'Observed legacy option prices are not asserted to be transaction prices.'])
    (output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
