"""Execute cells emitted by the maintained HFT1 generator, without JSON edits."""
from pathlib import Path
import json
import runpy
from layout import ROOT, FIGURES


def main():
    import matplotlib
    matplotlib.use('Agg')
    module = runpy.run_path(str(Path(__file__).with_name('hft1_generate_notebook.py')))
    namespace = {'__name__': '__main__'}
    from hft1_batched import scalar_mc, multi_mc
    for index, cell in enumerate(module['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            if 'def mc_compare_multi(' in source:
                source = source.replace('mc_MULTI = mc_compare_multi(P, P_MULTI, Sigma_multi, chol_multi)', 'mc_MULTI = multi_mc(P, P_MULTI, Sigma_multi, chol_multi)')
            if 'mc_BM = mc_compare(' in source:
                source = 'mc_BM = scalar_mc(P, seed=1000)'
            if 'mc_GBM = mc_compare(' in source:
                source = 'mc_GBM = scalar_mc(P, gbm=True, seed=2000)'
            namespace.update({'scalar_mc':scalar_mc,'multi_mc':multi_mc})
            exec(compile(source, f'generated_hft1_cell_{index}', 'exec'), namespace)
    from hft1_plot_multivariate import render
    render(namespace, FIGURES / 'hft1')
    import numpy as np
    output = ROOT / 'outputs' / 'hft1' / 'published-configuration'
    output.mkdir(parents=True,exist_ok=True)
    summary = {'configuration':'Supplied Article1 configuration:5000 scalar paths;3000 multivariate paths;rho_AB=.65,rho_AC=-.55,rho_BC=-.35. The preceding generator freeze remains separately preserved.',
               'scalar_paths':namespace['P']['N_MC'],'multiasset_paths':namespace['P_MULTI']['N_MC'],
               'multiasset_correlation':namespace['P_MULTI']['corr'].tolist(), 'statistics':namespace['st'],
               'multiasset_statistics':{key:{'mean':float(np.mean(value)), 'std':float(np.std(value))} for key,value in namespace['mc_MULTI'].items()}}
    for name in ['mc_BM','mc_GBM','mc_MULTI']:
        np.savez_compressed(output/(name+'.npz'),**namespace[name])
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('Classic HFT1 execution complete; outputs remain under the shared repository')
