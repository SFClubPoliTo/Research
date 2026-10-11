from __future__ import annotations

import pytest

from barrick_unified.cli import build_parser, select_team8_provider


def test_data_command_accepts_explicit_providers() -> None:
    assert build_parser().parse_args(["data", "--provider", "ib"]).provider == "ib"
    assert build_parser().parse_args(["data", "--provider", "lse"]).provider == "lse"


def test_interactive_provider_defaults_to_ib() -> None:
    assert select_team8_provider(lambda _: "") == "ib"
    assert select_team8_provider(lambda _: "LSE") == "lse"


def test_interactive_provider_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="Fonte non valida"):
        select_team8_provider(lambda _: "other")


def test_data_dispatch_forwards_arguments_without_requesting_quotes(monkeypatch):
    from barrick_unified import cli
    calls=[]
    monkeypatch.setattr(cli.UnifiedWorkflow,'run_entry_point',lambda self,name,args:calls.append((name,args)) or 0)
    assert cli.main(['data','--provider','ib','--','--help'])==0
    assert calls==[('data-ib',['--help'])]
