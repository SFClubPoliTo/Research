"""Shared stage dispatcher for Market Making completo."""
import argparse
import json
from pathlib import Path
import runpy
from layout import ROOT, FIGURES

STAGES = {'rough-figures': 'hft2_generate_article_figures', 'rough-hjb': 'hft2_solve_rough_hjb',
          'temporal-figures': 'hft3_temporal_policy', 'market': 'hft3_simulate_market',
          'multiasset': 'hft3_simulate_multiasset', 'audit': 'hft3_residual_audit', 'article-figures': 'figure_replay'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['status', 'run'])
    parser.add_argument('stage', nargs='?', choices=list(STAGES)+['classic'])
    args = parser.parse_args()
    if args.action == 'status':
        print(json.dumps({'project': 'Market Making completo', 'runtime_root': str(ROOT),
                          'stages': list(STAGES)+['classic'], 'reports': {v: (ROOT/'outputs'/f'report_{v}'/'Articolo.pdf').exists() for v in ['unificato', 'paper']},
                          'scientific_status': 'Synthetic models; covariance proxy is not fitted P3; no exchange latency claim'}, indent=2))
        return
    if args.stage is None:
        parser.error('run requires a stage')
    import sys
    if args.stage == 'article-figures':
        sys.argv = ['figure_replay', 'compute']
    elif args.stage == 'rough-figures':
        sys.argv = ['generate_article_figures', '--output', str(FIGURES/'hft2/generated')]
    else:
        sys.argv = [args.stage]
    if args.stage == 'classic':
        from hft1_run_classic import main as classic
        classic()
    else:
        runpy.run_module(STAGES[args.stage], run_name='__main__')


if __name__ == '__main__':
    main()
