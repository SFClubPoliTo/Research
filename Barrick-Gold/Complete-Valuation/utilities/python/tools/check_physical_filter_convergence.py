"""Evaluate frozen physical candidates; refinement does not refit parameters."""
import argparse,json
from pathlib import Path
from fit_physical_candidates import load_training,physical_filter,ROOT


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models',nargs='+',default=['heston','bates','full_bates_hawkes'])
    parser.add_argument('--substeps',nargs='+',type=int,default=[1,2,4,8])
    parser.add_argument('--output-name',default='20261006-filter-convergence')
    args=parser.parse_args()
    _,r,dt,carry=load_training()
    source=ROOT/'outputs/physical_measure/20261006-fixed-q-candidates'
    out=ROOT/'outputs/physical_measure'/args.output_name
    out.mkdir(parents=True,exist_ok=True)
    for model in args.models:
        fit=json.loads((source/(model+'.json')).read_text());rows=[]
        for substeps in args.substeps:
            for seed in [704,705,706]:
                result=physical_filter(r,dt,carry,fit['q_parameters'],fit['premia'],particles=4096,seed=seed,substeps=substeps,return_diagnostics=True)
                result.pop('log_scores');rows.append(dict(seed=seed,particles=4096,**result))
            print(model,substeps,[round(x['negative_log_likelihood'],3) for x in rows[-3:]],flush=True)
            (out/(model+'.json')).write_text(json.dumps(dict(status='NUMERICAL_DIAGNOSTIC_NOT_DCF_ADMITTED',model=model,parameter_source=fit['status'],checks=rows),indent=2),encoding='utf-8')


if __name__=='__main__':main()
