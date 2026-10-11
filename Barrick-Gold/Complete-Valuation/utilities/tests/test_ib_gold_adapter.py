from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from barrick_unified.ib_gold_adapter import (
    last_valid_bid_ask,
    parse_utc_timestamp,
    select_standard_monthly_chains,
    select_strikes,
    write_snapshot,
)
from barrick_unified.team8_rate_curve import manual_curve_frame


def test_timestamp_requires_timezone_and_normalises_to_utc() -> None:
    assert parse_utc_timestamp("2026-09-02T20:00:00Z").tzinfo == timezone.utc
    with pytest.raises(ValueError, match="timezone"):
        parse_utc_timestamp("2026-09-02T20:00:00")


def test_standard_monthly_selection_is_sorted_and_distinct() -> None:
    future_a = SimpleNamespace(lastTradeDateOrContractMonth="20261028")
    future_b = SimpleNamespace(lastTradeDateOrContractMonth="20261229")
    chain_a = SimpleNamespace(
        exchange="COMEX", tradingClass="OG", expirations={"20260924"}
    )
    chain_b = SimpleNamespace(
        exchange="COMEX", tradingClass="OG", expirations={"20261027", "20261124"}
    )
    weekly = SimpleNamespace(
        exchange="COMEX", tradingClass="G1R", expirations={"20260903"}
    )
    selected = select_standard_monthly_chains(
        [(future_b, [chain_b]), (future_a, [chain_a, weekly])],
        datetime(2026, 9, 2, 20, tzinfo=timezone.utc),
        max_maturities=2,
    )
    assert [row[2] for row in selected] == ["20260924", "20261027"]


def test_strikes_are_listed_bounded_and_capped() -> None:
    strikes = list(range(50, 151))
    selected = select_strikes(strikes, forward=100.0, log_moneyness_limit=0.10, max_strikes=7)
    assert len(selected) == 7
    assert selected == sorted(selected)
    assert all(abs(__import__("math").log(strike / 100.0)) <= 0.10 for strike in selected)


def test_last_valid_bid_ask_rejects_future_and_crossed_quotes() -> None:
    snapshot = datetime(2026, 9, 2, 20, tzinfo=timezone.utc)
    ticks = [
        SimpleNamespace(
            time=datetime(2026, 9, 2, 19, 59, 58, tzinfo=timezone.utc),
            priceBid=10.0, priceAsk=11.0, sizeBid=2, sizeAsk=3,
        ),
        SimpleNamespace(
            time=datetime(2026, 9, 2, 19, 59, 59, tzinfo=timezone.utc),
            priceBid=12.0, priceAsk=11.0, sizeBid=2, sizeAsk=3,
        ),
        SimpleNamespace(
            time=datetime(2026, 9, 2, 20, 0, 1, tzinfo=timezone.utc),
            priceBid=11.0, priceAsk=12.0, sizeBid=2, sizeAsk=3,
        ),
    ]
    selected = last_valid_bid_ask(ticks, snapshot)
    assert selected is not None
    assert selected["bid"] == 10.0
    assert selected["ask"] == 11.0
    assert selected["mid"] == 10.5


def test_manual_curve_is_locked_to_approved_input() -> None:
    curve = manual_curve_frame()
    assert len(curve) == 14
    assert set(curve["curve_date"]) == {"2026-09-02"}
    assert curve["par_yield_decimal"].iloc[[0, -1]].tolist() == [0.0383, 0.0527]


def test_snapshot_writer_refuses_to_overwrite(tmp_path) -> None:
    output = tmp_path / "existing"
    output.mkdir()
    (output / "sentinel.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        write_snapshot(output, None, None, {})
