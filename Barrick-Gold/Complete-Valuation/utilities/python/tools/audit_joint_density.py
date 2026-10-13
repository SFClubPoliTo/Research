"""Evaluate the restricted-family finite-horizon entropy bound on dated fits."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
sys.path.insert(0, str(ROOT/'utilities/python'))
from barrick_unified.physical_measure import restricted_joint_entropy_bound


def main():
    sources = list((ROOT/'outputs/physical_measure/20261006-fixed-q-candidates').glob('*.json'))
    sources += list((ROOT/'outputs/physical_measure/20261007-refit-resolution-heston').glob('*.json'))
    results=[]
    for source in sorted(sources):
        fit=json.loads(source.read_text(encoding='utf-8'))
        q=fit['q_parameters'];eta,log_k,log_c,mark_shift=fit['premia']
        std=q.get('sigma_J',0.)
        baseline=q.get('lambda_bar',q.get('lambd',0.))
        result=restricted_joint_entropy_bound(
            horizon=5.,variance0=q['v0'],kappa_q=q['kappa'],theta_q=q['theta'],
            xi=q['xi'],rho=q['rho'],eta_price=eta,
            eta_variance=q['kappa']*(1-np.exp(log_k))/q['xi'],
            lambda0=q.get('lambda0',baseline),baseline=baseline,
            alpha=q.get('alpha',0.),beta=q.get('beta',0.),
            intensity_ratio=np.exp(log_c),mark_tilt=mark_shift/std if std else 0.,
            mark_std=std)
        results.append(dict(model=fit['model'],parameter_source=source.relative_to(ROOT).as_posix(),
                            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),**result))
    output=ROOT/'outputs/physical_measure/20261007-joint-density'
    output.mkdir(exist_ok=True)
    (output/'summary.json').write_text(json.dumps(dict(
        status='EXACT_RESTRICTED_FAMILY_BOUND_NOT_EMPIRICAL_ADMISSION',checks=results,
        proof='utilities/docs/RESTRICTED-JOINT-DENSITY.md'),indent=2)+'\n',encoding='utf-8')
    print(json.dumps([dict(model=r['model'],bound=r['entropy_upper_bound']) for r in results]))


if __name__ == '__main__':
    main()
