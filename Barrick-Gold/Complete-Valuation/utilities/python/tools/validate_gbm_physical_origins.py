"""Exact conditional GBM P forecasts with a freshly fitted Q sigma per origin."""
import argparse
from dataclasses import asdict
import hashlib
import json

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.special import ndtr
from scipy.stats import norm

from fit_physical_candidates import ROOT, load_training
from barrick_unified.physical_gbm import fit_gbm, predictive_log_score


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    if '/' in args.run_id or '\\' in args.run_id or args.run_id in ['.', '..', '']:
        parser.error('run-id must be a single directory name')
    output = ROOT/'outputs/physical_measure'/args.run_id
    if output.exists():
        parser.error('refusing to overwrite an experiment')
    output.mkdir(parents=True)
    history, returns, dt, _ = load_training()
    records = []
    for source in sorted((ROOT/'data/raw/ib_local/gold_origin_surfaces_20261007').glob('*.csv')):
        origin = pd.Timestamp(source.stem)
        frame = pd.read_csv(source)
        if not (pd.to_datetime(frame.date) == origin).all() or (pd.to_datetime(frame.curve_date) > origin).any():
            raise ValueError('invalid origin surface date')
        indices = np.flatnonzero((history.date == origin).to_numpy())
        if len(indices) != 1:
            raise ValueError('missing unique origin in RTH history')
        index = int(indices[0])
        if index+1 >= len(history):
            continue
        spot = float(frame.spot.iloc[0])
        if not np.allclose(frame.spot, history.close.iloc[index], rtol=0, atol=1e-8):
            raise ValueError('RTH and option spot mismatch')
        strike, maturity, rate, price, vega = [frame[c].to_numpy(float) for c in ['K','T','rate','price','vega']]

        def loss(sigma):
            root = sigma*np.sqrt(maturity)
            d1 = (np.log(spot/strike)+(rate+.5*sigma*sigma)*maturity)/root
            model = spot*ndtr(d1)-strike*np.exp(-rate*maturity)*ndtr(d1-root)
            return float(np.mean(((model-price)/np.maximum(vega, 1e-4))**2))

        calibration = minimize_scalar(loss, bounds=(.01, 3.), method='bounded', options={'xatol':1e-10})
        fit = fit_gbm(returns[:index], dt[:index], sigma_q=float(calibration.x))
        horizon = float(dt[index])
        mean = spot*np.exp(fit.arithmetic_drift*horizon)
        quantiles = spot*np.exp(fit.log_drift*horizon+fit.sigma*np.sqrt(horizon)*norm.ppf([.025,.1,.5,.9,.975]))
        target = float(history.close.iloc[index+1])
        # Log-price density transformed to price density with its Jacobian.
        score = predictive_log_score(np.log(target/spot), horizon, fit)-np.log(target)
        records.append(dict(origin=source.stem, target_date=str(history.date.iloc[index+1].date()),
                            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                            q_sigma=float(calibration.x), q_loss=float(calibration.fun),
                            q_success=bool(calibration.success), p_fit=asdict(fit),
                            forecast_mean=float(mean), target=target, quantiles=quantiles.tolist(),
                            error=float(mean-target), no_change_error=spot-target,
                            price_log_score=float(score),
                            coverage95=bool(quantiles[0]<=target<=quantiles[-1])))
    summary = dict(status='CONDITIONAL_TWO_STAGE_GBM_OOS_NOT_DCF_ADMITTED', targets=len(records),
                   first_origin=records[0]['origin'], last_origin=records[-1]['origin'],
                   rmse=float(np.sqrt(np.mean([r['error']**2 for r in records]))),
                   no_change_rmse=float(np.sqrt(np.mean([r['no_change_error']**2 for r in records]))),
                   mean_price_log_score=float(np.mean([r['price_log_score'] for r in records])),
                   coverage95=float(np.mean([r['coverage95'] for r in records])),
                   source_code_sha256=hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest(),
                   limitations=['Short historical option window; no 90-day targets within freeze.',
                     'Conditional origin Q diffusion held constant over P training and forecast.',
                     'Plug-in intervals omit structural parameter, drift and state uncertainty.',
                     'Exact GBM prediction removes simulation error, not model misspecification.',
                     'GLD USD/share, before gold basis, realized sales and FCFF.'])
    (output/'origins.json').write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')
    (output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
