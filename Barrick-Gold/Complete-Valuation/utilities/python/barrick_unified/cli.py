"""Command-line interface for the unified Barrick project facade."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Sequence

from .project import UnifiedWorkflow


def select_team8_provider(prompt: Callable[[str], str] = input) -> str:
    """Choose an acquisition adapter; instrument identities stay provider-specific."""
    provider = prompt('Data source [ib/lse, default ib]: ').strip().lower() or 'ib'
    if provider not in {'ib', 'lse'}:
        raise ValueError('Fonte non valida: choose ib or lse')
    return provider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="Override project-root discovery.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Print a read-only handoff audit.")
    data_parser = subparsers.add_parser('data', help='Run an explicit option acquisition adapter; inspect its instrument and date settings.')
    data_parser.add_argument('--provider', choices=['ib', 'lse'])
    data_parser.add_argument('arguments', nargs=argparse.REMAINDER)
    test_parser = subparsers.add_parser("test", help="Run the offline test suite.")
    test_parser.add_argument("pytest_args", nargs=argparse.REMAINDER)
    run_parser = subparsers.add_parser("run", help="Run an established project entry point.")
    run_parser.add_argument("name", choices=sorted(UnifiedWorkflow.ENTRY_POINTS))
    run_parser.add_argument("arguments", nargs=argparse.REMAINDER)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workflow = UnifiedWorkflow(args.root)
    if args.command == 'data':
        provider = args.provider or select_team8_provider()
        arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
        return workflow.run_entry_point('data-' + provider, arguments)
    if args.command == "status":
        workflow.print_status()
        return 0 if workflow.status()["status"] == "READY" else 1
    if args.command == "test":
        return workflow.run_tests(args.pytest_args)
    return workflow.run_entry_point(args.name, args.arguments)


if __name__ == "__main__":
    raise SystemExit(main())
