"""Symbol search, the polled quote set and the chart series, all read off the buffers.

Three routes, and between them they are everything the frontend needs to show a price.

**Nothing here computes a session figure.** `day change %` is read through
`RingBuffer.day_change_pct` and nothing else. A route recomputing it would be a second
definition of the same term, free to disagree with the first, and the surfaces that sort
by day change would then disagree with the surface that displays it.

**`GET /symbols` with no query is the metadata call.** It returns the whole universe with
each entry's name, sector, currency and decimal places, which is how the markets table
loads its static columns once at load rather than on every poll. That is not a
convenience — a table refetching 45 names twice a second is the defect it avoids.

**An unknown timeframe is rejected, not defaulted.** `Timeframe` is a `StrEnum` declared
on the route, so FastAPI answers an unknown `tf` with a 422 before the handler runs.
Silently falling back to 1m would show a chart that disagrees with its own toggle.
"""

from enum import StrEnum

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.buffer import SESSION_TICKS, Bar, RingBuffer
from app.instruments import Instrument
from app.models import Candle, Quote, SymbolMatch
from app.state import AppState, get_state

router = APIRouter(tags=["market"])

#: Closes carried on a quote for the row sparkline. Enough to read as a trend at the
#: width the design gives it, and short enough that 45 of them are not a large payload.
SPARKLINE_POINTS = 24


class Timeframe(StrEnum):
    """The four chart timeframes. Declared as a type so an unknown one is a 422."""

    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    SESSION = "session"


#: How many one-minute bars aggregate into one bar of each timeframe. A session is 390
#: ticks, the same 390 the session-relative queries use, taken from `app.buffer` rather
#: than restated.
AGGREGATION: dict[Timeframe, int] = {
    Timeframe.ONE_MINUTE: 1,
    Timeframe.FIVE_MINUTES: 5,
    Timeframe.FIFTEEN_MINUTES: 15,
    Timeframe.SESSION: SESSION_TICKS,
}


@router.get("/symbols", response_model=list[SymbolMatch], operation_id="listSymbols")
def get_symbols(
    q: str = Query(default="", description="Partial symbol or name; empty returns all."),
    state: AppState = Depends(get_state),
) -> list[SymbolMatch]:
    """Instruments matching `q` on symbol or name, or the whole universe when it is empty.

    The match is a case-insensitive substring over both fields, so `oc` finds Occidental
    by name and `XO` finds XOM by symbol, while a string in neither is absent from the
    result rather than ranked low.
    """
    needle = q.strip().lower()
    return [
        _symbol_match(instrument)
        for instrument in state.instruments.values()
        if not needle
        or needle in instrument.symbol.lower()
        or needle in instrument.name.lower()
    ]


@router.get("/quotes", response_model=list[Quote], operation_id="listQuotes")
def get_quotes(
    symbols: str = Query(description="Comma-separated symbols, in the order wanted."),
    state: AppState = Depends(get_state),
) -> list[Quote]:
    """One quote per requested symbol, **in request order**.

    The client selects from this list positionally, so the order is the contract. An
    unknown symbol is a 404 naming it rather than a silently shorter list, which would
    misalign every subsequent entry.
    """
    requested = [one.strip() for one in symbols.split(",") if one.strip()]
    unknown = [one for one in requested if one not in state.instruments]
    if unknown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown symbols: {unknown}.",
        )
    return [_quote(symbol, state.buffers[symbol]) for symbol in requested]


@router.get(
    "/candles/{symbol}", response_model=list[Candle], operation_id="listCandles"
)
def get_candles(
    symbol: str,
    tf: Timeframe = Query(default=Timeframe.ONE_MINUTE, description="Chart timeframe."),
    state: AppState = Depends(get_state),
) -> list[Candle]:
    """The instrument's history aggregated into bars of the requested timeframe.

    Bars are grouped by tick index rather than by position, so a group is the same set
    of ticks whatever the buffer happens to hold — and the open, high, low, close and
    volume of a group are the first open, the highest high, the lowest low, the last
    close and the summed volume of its constituents.
    """
    buffer = state.buffers.get(symbol)
    if buffer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown symbol: {symbol!r}."
        )
    return _aggregate(buffer.bars(), AGGREGATION[tf])


def _symbol_match(instrument: Instrument) -> SymbolMatch:
    return SymbolMatch(
        symbol=instrument.symbol,
        name=instrument.name,
        sector=instrument.sector,
        currency=instrument.currency,
        decimals=instrument.decimals,
    )


def _quote(symbol: str, buffer: RingBuffer) -> Quote:
    """One quote, with day change read through the buffer's own definition."""
    bars = buffer.bars()
    return Quote(
        symbol=symbol,
        last=buffer.latest().close,
        day_change_pct=buffer.day_change_pct(),
        # Oldest first, latest last, prices rather than returns — the shape the
        # contract states and the row sparkline draws on its own scale.
        sparkline=[bar.close for bar in bars[-SPARKLINE_POINTS:]],
    )


def _aggregate(bars: tuple[Bar, ...], factor: int) -> list[Candle]:
    """Group `bars` into candles of `factor` ticks each, keyed by tick index."""
    if not bars:
        return []
    groups: dict[int, list[Bar]] = {}
    for bar in bars:
        groups.setdefault(bar.t // factor, []).append(bar)
    return [
        Candle(
            t=group[0].t,
            open=group[0].open,
            high=max(bar.high for bar in group),
            low=min(bar.low for bar in group),
            close=group[-1].close,
            volume=sum(bar.volume for bar in group),
        )
        for _, group in sorted(groups.items())
    ]
