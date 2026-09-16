"""The market routes' outcome clauses, each asserted against something that can fail.

Three of these exist because nothing else in the suite reads what they cover:

* **the empty-`q` call** — without it `GET /symbols` could return an empty list, or
  entries missing `sector`, `currency` or `decimals`, and every other assertion here
  would still pass. It is also the call the markets table loads its static columns from,
  so it is the one clause a later task depends on outright.
* **the inclusion half of the match** — asserting only that a known non-match is
  excluded is satisfied by a matcher that returns nothing for every query.
* **the sparkline** — nothing else touches it, so a `Quote` carrying an empty list would
  pass unnoticed.

No price-level literal is asserted anywhere. Day change is checked by agreement with
`RingBuffer.day_change_pct` rather than against a number, which is the property that
matters: every surface reads the same definition.
"""

import pytest
from fastapi.testclient import TestClient

from app import state as state_module
from app.buffer import SESSION_TICKS
from app.main import app
from app.routers.market import SPARKLINE_POINTS
from app.state import build_state


def report(capsys, message: str) -> None:
    """Print through pytest's capture, so a count survives a passing run."""
    with capsys.disabled():
        print(f"\n    {message}")


@pytest.fixture(scope="module")
def state():
    """One backfilled state for the module: 780 ticks is slow to build per test."""
    built = build_state()
    return built


@pytest.fixture(scope="module")
def client(state):
    """A client whose routes resolve against the module's state."""
    state_module._state = state
    with TestClient(app) as test_client:
        yield test_client
    state_module._state = None


# ── GET /symbols ────────────────────────────────────────────────────────────


def test_empty_query_returns_the_whole_universe_with_its_metadata(
    client, state, capsys
) -> None:
    """The metadata call: every instrument, every static column populated.

    This is how the markets table loads name, sector, currency and decimals once at
    load instead of on every poll, so an empty list or a missing column here breaks a
    later task rather than this one.
    """
    for query in ("", "   "):
        response = client.get("/symbols", params={"q": query})
        assert response.status_code == 200
        body = response.json()
        assert len(body) == len(state.instruments)
        for entry in body:
            assert entry["name"], f"{entry['symbol']} has no name"
            assert entry["sector"], f"{entry['symbol']} has no sector"
            assert entry["currency"], f"{entry['symbol']} has no currency"
            assert isinstance(entry["decimals"], int)

    omitted = client.get("/symbols")
    assert omitted.status_code == 200
    assert len(omitted.json()) == len(state.instruments)

    report(capsys, f"empty q returned {len(omitted.json())} instruments, all populated")


def test_the_match_includes_a_partial_symbol_and_a_partial_name(
    client, state, capsys
) -> None:
    """Both halves of the match, named. Exclusion alone is met by matching nothing."""
    target = next(iter(state.instruments.values()))

    by_symbol = client.get("/symbols", params={"q": target.symbol[:2].lower()}).json()
    assert target.symbol in {entry["symbol"] for entry in by_symbol}

    name_fragment = target.name.split()[0][:4].lower()
    by_name = client.get("/symbols", params={"q": name_fragment}).json()
    assert target.symbol in {entry["symbol"] for entry in by_name}

    report(
        capsys,
        f"{target.symbol} found by partial symbol {target.symbol[:2].lower()!r} "
        f"and by partial name {name_fragment!r}",
    )


def test_the_match_excludes_a_known_non_match(client, capsys) -> None:
    """A string in no symbol and no name returns nothing."""
    body = client.get("/symbols", params={"q": "zzqx"}).json()
    assert body == []
    report(capsys, "query 'zzqx' excluded every instrument")


# ── GET /quotes ─────────────────────────────────────────────────────────────


def test_quote_order_follows_request_order(client, state, capsys) -> None:
    """Deliberately unsorted, because the client selects from this list positionally."""
    symbols = list(state.instruments)[:6]
    scrambled = [symbols[3], symbols[0], symbols[5], symbols[1]]

    body = client.get("/quotes", params={"symbols": ",".join(scrambled)}).json()

    assert [entry["symbol"] for entry in body] == scrambled
    report(capsys, f"requested {scrambled} and received them in that order")


def test_day_change_equals_the_buffer_definition(client, state) -> None:
    """The route reads `RingBuffer.day_change_pct` rather than recomputing it."""
    symbols = list(state.instruments)[:8]
    body = client.get("/quotes", params={"symbols": ",".join(symbols)}).json()

    for entry in body:
        expected = state.buffers[entry["symbol"]].day_change_pct()
        assert entry["day_change_pct"] == pytest.approx(expected)


def test_every_quote_carries_a_sparkline_ending_at_the_latest_close(
    client, state, capsys
) -> None:
    """Nothing else reads the sparkline, so an empty list would pass unnoticed."""
    symbols = list(state.instruments)[:5]
    body = client.get("/quotes", params={"symbols": ",".join(symbols)}).json()

    for entry in body:
        spark = entry["sparkline"]
        assert spark, f"{entry['symbol']} carries an empty sparkline"
        assert len(spark) <= SPARKLINE_POINTS
        assert all(isinstance(point, float) for point in spark)
        assert spark[-1] == pytest.approx(entry["last"]), (
            "the sparkline is oldest first with the latest close last"
        )

    report(capsys, f"sparklines carried {len(body[0]['sparkline'])} closes, latest last")


def test_every_quote_carries_its_session_volume(client, state, capsys) -> None:
    """The markets table's volume column binds this.

    Added after that column was found rendering `0` for all forty-five rows: `Quote`
    carried no volume, so the component had nothing to bind and a placeholder shipped.
    Nothing else in this suite reads the field, so without this assertion it could
    silently go missing again.
    """
    symbols = list(state.instruments)[:6]
    body = client.get("/quotes", params={"symbols": ",".join(symbols)}).json()

    for entry in body:
        expected = state.buffers[entry["symbol"]].session_volume()
        assert entry["session_volume"] == pytest.approx(expected)
        assert entry["session_volume"] > 0.0, f"{entry['symbol']} reports no volume"

    report(capsys, f"session volume served for {len(body)} symbols, all non-zero")


def test_an_unknown_symbol_is_rejected_rather_than_silently_dropped(client) -> None:
    """A shorter list would misalign every entry after the missing one."""
    response = client.get("/quotes", params={"symbols": "NOPE"})
    assert response.status_code == 404


# ── GET /candles ────────────────────────────────────────────────────────────


def test_each_timeframe_returns_a_count_consistent_with_its_aggregation(
    client, state, capsys
) -> None:
    """Coarser timeframes return fewer bars, in the ratio their factors imply."""
    symbol = next(iter(state.instruments))
    counts = {}
    for tf in ("1m", "5m", "15m", "session"):
        body = client.get(f"/candles/{symbol}", params={"tf": tf}).json()
        counts[tf] = len(body)

    held = len(state.buffers[symbol].bars())
    assert counts["1m"] == held
    for tf, factor in (("5m", 5), ("15m", 15), ("session", SESSION_TICKS)):
        assert counts[tf] == pytest.approx(held / factor, abs=1), (
            f"{tf} grouped {held} bars into {counts[tf]}"
        )
    assert counts["1m"] > counts["5m"] > counts["15m"] > counts["session"]

    report(capsys, f"{held} bars aggregated to {counts}")


def test_an_unknown_timeframe_is_rejected_rather_than_defaulted(client, state) -> None:
    """422 before the handler runs, because `tf` is typed on the route."""
    symbol = next(iter(state.instruments))
    response = client.get(f"/candles/{symbol}", params={"tf": "4h"})
    assert response.status_code == 422


def test_a_candle_group_summarises_its_constituents(client, state) -> None:
    """Open from the first, close from the last, high and low across the group."""
    symbol = next(iter(state.instruments))
    body = client.get(f"/candles/{symbol}", params={"tf": "5m"}).json()

    for candle in body[:20]:
        assert candle["high"] >= candle["open"]
        assert candle["high"] >= candle["close"]
        assert candle["low"] <= candle["open"]
        assert candle["low"] <= candle["close"]
        assert candle["volume"] > 0.0
