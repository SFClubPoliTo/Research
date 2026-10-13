"""Chronological initialization; guesses never substitute for a current fit."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def previous_fit(directory, origin, model, *, physical=False):
    """Latest successful strictly earlier artifact in this experiment only."""
    origin = pd.Timestamp(origin)
    for path in sorted(Path(directory).glob('*.json'), reverse=True):
        try:
            date = pd.Timestamp(path.stem)
        except ValueError:
            continue
        if date >= origin:
            continue
        record = json.loads(path.read_text(encoding='utf-8'))
        success_key = 'optimizer_success' if physical else 'success'
        expected = ('CONDITIONAL_TWO_STAGE_OOS_NOT_DCF_ADMITTED' if physical
                    else 'DATED_Q_CALIBRATION_NOT_PHYSICAL_FORECAST')
        if (record.get('model') != model or record.get('origin') != path.stem
                or record.get('status') != expected or not record.get(success_key)):
            continue
        return record, dict(origin=path.stem, source_file=path.name,
                           source_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return None, None


def parameter_vector(params, model):
    diffusion = [params[key] for key in ['v0', 'kappa', 'theta']]
    diffusion += [params.get('xi', params.get('sigma')), params['rho']]
    if model == 'heston':
        return np.asarray(diffusion, dtype=float)
    if model == 'bates':
        return np.asarray(diffusion+[params[k] for k in ['lambd','mu_J','sigma_J']], dtype=float)
    return np.asarray(diffusion+[params[k] for k in
        ['lambda0','lambda_bar','branching_ratio','beta','mu_J','sigma_J']], dtype=float)
