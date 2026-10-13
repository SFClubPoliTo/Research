"""Matched-origin physical price forecast metrics with explicit support."""
import numpy as np


def summarize_matched_origins(experiments):
    """Compare completed predictions only on identical origin/target pairs.

    Every model's full support is recorded. An incomplete experiment is not
    silently promoted to the full origin panel, nor are failed optimizers
    discarded after observing their forecast errors.
    """
    if not experiments or any(not rows for rows in experiments.values()):
        raise ValueError('nonempty model experiments required')
    indexed = {}
    for model, rows in experiments.items():
        mapping = {}
        for row in rows:
            key = (row['origin'], row['target_date'])
            if key[1] <= key[0] or key in mapping:
                raise ValueError('future targets and unique origin/target pairs required')
            if 'training_last' in row and row['training_last'] > key[0]:
                raise ValueError('training extends beyond origin')
            predicted = row.get('predictive_mean', row.get('forecast_mean'))
            quantiles = row.get('predictive_quantiles', row.get('quantiles'))
            values = np.asarray([predicted,row['target'],row['no_change_error'],*quantiles],float)
            if len(quantiles) != 5 or not np.isfinite(values).all() or np.any(np.diff(quantiles)<0):
                raise ValueError('finite forecast and five ordered predictive quantiles required')
            mapping[key] = (row, float(predicted), np.asarray(quantiles))
        indexed[model] = mapping
    common = sorted(set.intersection(*(set(value) for value in indexed.values())))
    if not common:
        raise ValueError('no common completed forecast origins')
    models = {}
    reference_targets = reference_no_change = None
    for model, mapping in indexed.items():
        rows = [mapping[key] for key in common]
        target = np.array([row[0]['target'] for row in rows])
        no_change = np.array([row[0]['no_change_error'] for row in rows])
        if reference_targets is None:
            reference_targets, reference_no_change = target, no_change
        elif not np.allclose(target, reference_targets, atol=1e-8, rtol=0) or not np.allclose(no_change,reference_no_change,atol=1e-8,rtol=0):
            raise ValueError('models do not share target values and no-change baseline')
        error = np.array([row[1]-row[0]['target'] for row in rows])
        quantiles = np.array([row[2] for row in rows])
        optimizer = [row[0].get('p_optimizer_success',row[0].get('optimizer_success')) for row in rows]
        models[model] = dict(total_completed=len(mapping),matched=len(common),
             unmatched=len(mapping)-len(common),rmse=float(np.sqrt(np.mean(error**2))),
             mae=float(np.mean(abs(error))),mean_error=float(error.mean()),
             mean_squared_loss_difference_vs_no_change=float(np.mean(error**2-no_change**2)),
             coverage95=float(np.mean((quantiles[:,0]<=target)&(target<=quantiles[:,4]))),
             coverage80=float(np.mean((quantiles[:,1]<=target)&(target<=quantiles[:,3]))),
             p_optimizer_failures=sum(value is False for value in optimizer),
             p_optimizer_status_not_applicable_or_unrecorded=sum(value is None for value in optimizer))
    return dict(status='MATCHED_PHYSICAL_FORECAST_DIAGNOSTIC_NOT_DCF_ADMITTED',
                common_targets=len(common),common_pairs=[list(key) for key in common],
                no_change_rmse=float(np.sqrt(np.mean(reference_no_change**2))),models=models,
                interpretation='Descriptive paired losses; no significance or model-selection claim. GLD USD/share.')
