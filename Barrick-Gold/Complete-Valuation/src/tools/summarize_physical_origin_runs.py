"""Freeze matched metrics from completed dated physical forecast files."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
sys.path.insert(0,str(ROOT/'src'))
from barrick_unified.physical_oos_summary import summarize_matched_origins


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--experiment',action='append',required=True,
                        help='MODEL=RUN_DIRECTORY; repeat to combine interrupted parts')
    args=parser.parse_args()
    if Path(args.run_id).name!=args.run_id or args.run_id in ['.','..']:
        parser.error('run-id must be a directory name')
    output=ROOT/'outputs/physical_measure'/args.run_id
    if output.exists():
        parser.error('refusing to overwrite frozen metrics')
    experiments={};inputs=[]
    for value in args.experiment:
        model,run=value.split('=',1)
        if Path(run).name!=run or run in ['.','..']:
            parser.error('input run must be a directory name')
        directory=ROOT/'outputs/physical_measure'/run
        for source in sorted(directory.glob('*.json')):
            if source.name=='summary.json':
                continue
            payload=json.loads(source.read_text(encoding='utf-8'))
            rows=payload if isinstance(payload,list) else [payload]
            if not rows or any('origin' not in row or 'target_date' not in row for row in rows):
                continue
            experiments.setdefault(model,[]).extend(rows)
            inputs.append(dict(path=source.relative_to(ROOT).as_posix(),
                               sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    expected={value.split('=',1)[0] for value in args.experiment}
    if set(experiments)!=expected:
        parser.error('one or more requested models have no completed forecast')
    result=summarize_matched_origins(experiments)
    result['inputs']=inputs
    result['requested_experiments']=args.experiment
    result['source_code_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output.mkdir(parents=True)
    (output/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','common_pairs']},indent=2))


if __name__=='__main__':
    main()
