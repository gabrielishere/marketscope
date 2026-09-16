"""The three ranked lists and the five macro drivers.

**The API's ordering is the contract.** The client applies no sort of its own, because a
component re-sorting these lists would silently mask a defect here — the screen would
look right while the ranking was wrong. So the order these routes return is the order
that renders.

**Gainers and losers are disjoint by construction.** They are the two ends of one sorted
sequence, taken from opposite sides, and the split refuses to overlap rather than
trusting the list to be long enough.

**Macro drivers come back in factor order** — `market`, `rates`, `oil`, `usd`, `credit` —
which is the order the strip renders and the order an instrument's betas are held in.
Nothing sorts them by price or by move.
"""

from fastapi import APIRouter, Depends

from app.buffer import FACTORS
from app.instruments import Instrument
from app.models import MacroDriver, Mover, MoversResponse
from app.state import AppState, get_state

router = APIRouter(tags=["movers"])

#: Rows per ranked list. Three lists of five read at a glance; longer and the panel
#: stops being a summary.
LIST_SIZE = 5


@router.get("/movers", response_model=MoversResponse, operation_id="getMovers")
def get_movers(state: AppState = Depends(get_state)) -> MoversResponse:
    """Gainers, losers and most active, each already in the order it renders in."""
    rows = [_mover(symbol, state) for symbol in state.instruments]

    by_change = sorted(rows, key=lambda row: row.day_change_pct, reverse=True)
    # Taken from the two ends of one sequence and split in the middle, so the lists
    # cannot overlap even when the universe is smaller than twice LIST_SIZE.
    split = min(LIST_SIZE, len(by_change) // 2)
    gainers = by_change[:split]
    losers = list(reversed(by_change[-split:])) if split else []

    by_volume = sorted(rows, key=lambda row: row.session_volume, reverse=True)
    return MoversResponse(
        gainers=gainers, losers=losers, most_active=by_volume[:LIST_SIZE]
    )


@router.get("/macro", response_model=list[MacroDriver], operation_id="listMacroDrivers")
def get_macro(state: AppState = Depends(get_state)) -> list[MacroDriver]:
    """The five macro drivers, one per factor, in factor order.

    Ordered by iterating `FACTORS` rather than by filtering the universe, so the result
    follows the factor order whatever order the data file happens to list them in.
    """
    drivers = {
        instrument.factor: instrument
        for instrument in state.instruments.values()
        if instrument.is_macro_driver
    }
    return [_macro_driver(drivers[factor], state) for factor in FACTORS]


def _mover(symbol: str, state: AppState) -> Mover:
    buffer = state.buffers[symbol]
    return Mover(
        symbol=symbol,
        last=buffer.latest().close,
        day_change_pct=buffer.day_change_pct(),
        session_volume=buffer.session_volume(),
    )


def _macro_driver(instrument: Instrument, state: AppState) -> MacroDriver:
    buffer = state.buffers[instrument.symbol]
    assert instrument.factor is not None  # a macro driver carries one by definition
    return MacroDriver(
        symbol=instrument.symbol,
        name=instrument.name,
        factor=instrument.factor,
        last=buffer.latest().close,
        day_change_pct=buffer.day_change_pct(),
    )
