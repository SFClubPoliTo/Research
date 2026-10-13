from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from layout import ROOT, OUTPUTS, FIGURES


def main():
    directory=OUTPUTS/'validation/20261013-refinement'
    d=pd.read_csv(directory/'baseline.csv',float_precision='round_trip')
    results=[]
    for study in [0,1,2]:
        group=d[d.study==study]
        key=['requested_steps','domain','points'][study]
        reference=group[group[key]==group[key].max()]
        for configuration in sorted(group[key].unique()):
            candidate=group[group[key]==configuration]
            errors={'theta':0.,'bid':0.,'ask':0.}
            for (t,q),block in candidate.groupby(['t','q']):
                if t==1:continue
                ref=reference[(reference.t==t)&(reference.q==q)]
                for metric in errors:
                    valid=ref[metric].notna()
                    if valid.any():
                        candidate_valid=block[metric].notna()
                        if not candidate_valid.any():continue
                        # Evaluate both resolutions on the same strict interior points;
                        # do not clamp a coarse endpoint to the truncated fine-grid support.
                        left=max(block.y[candidate_valid].min(),ref.y[valid].min())
                        right=min(block.y[candidate_valid].max(),ref.y[valid].max())
                        common=np.linspace(left,right,201)
                        prediction=np.interp(common,ref.y[valid],ref[metric][valid])
                        candidate_value=np.interp(common,block.y[candidate_valid],block[metric][candidate_valid])
                        diff=abs(candidate_value-prediction)
                        if np.isfinite(diff).any():errors[metric]=max(errors[metric],float(np.nanmax(diff)))
            results.append({'study':['temporal','fixed_spacing_domain','spatial'][study],'configuration':int(configuration),'errors_against_finest':errors})
    (directory/'summary.json').write_text(json.dumps({'comparisons':results,'scope':'Interior |Y|<=2 SD, t=0/.5, every admissible inventory; differences not exact error bounds'},indent=2),encoding='utf-8')
    terminal=pd.read_csv(OUTPUTS/'hft3/multiasset/rho0.7_n3900_terminal.csv')
    a=terminal.pnl_sep.to_numpy();b=terminal.pnl_cov.to_numpy()
    def ce(v):return -np.log(np.mean(np.exp(-.2*v),axis=-1))/.2
    rng=np.random.default_rng(20261013)
    boot=rng.integers(0,len(a),(10000,len(a)))
    delta=ce(b[boot])-ce(a[boot])
    report={'method':'paired percentile bootstrap, fixed synthetic run; conditional sampling uncertainty only','resamples':10000,'seed':20261013,'ce_difference':float(ce(b)-ce(a)),'ce_difference_95_interval':np.quantile(delta,[.025,.975]).tolist()}
    (OUTPUTS/'validation/cara-bootstrap.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    audit=json.loads((OUTPUTS/'validation/20261013-full-residual/summary.json').read_text())
    f=FIGURES/'shared';f.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    axes[0].bar(['Reduced sum','Full separate','Full proxy'],[audit[k]['rms'] for k in ['reduced_sum','full_separate','full_covariance_proxy']],color=['#9fa8ad','#126a83','#a44146'])
    axes[0].set(ylabel='RMS HJB residual',title='Off-grid derivative-reconstruction diagnostic')
    for study,marker in [('temporal','o'),('fixed_spacing_domain','s'),('spatial','^')]:
        rows=[r for r in results if r['study']==study]
        axes[1].plot([str(r['configuration']) for r in rows],[r['errors_against_finest']['theta'] for r in rows],marker=marker,label=study)
    axes[1].set(ylabel='Max value difference',title='Independent refinement directions')
    axes[1].legend(fontsize=7);axes[1].grid(alpha=.2)
    fig.savefig(f/'validation.png',dpi=180);plt.close(fig)
    print(json.dumps({'refinement':results,'cara':report},indent=2))


if __name__=='__main__':main()
