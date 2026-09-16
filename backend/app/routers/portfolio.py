"""The paper portfolio: the fixed positions and one set of totals.

Read-only. There is no trade endpoint in this build — the demo is about a world event
moving a market, and nobody watching one places an order.

**One set of totals, not one per currency.** Every instrument is denominated in the same
currency and there is no FX rate anywhere, so there is nothing to sum across and no
per-currency breakdown to give. `PortfolioTotals` is a single object for that reason.

**Day change is read through the buffer.** `RingBuffer.day_change_pct` is the one
definition; a total computed from a second one would disagree with the watchlist showing
the same instruments.
"""

from fastapi import APIRouter, Depends

from app.models import PortfolioResponse, PortfolioTotals, Position
from app.state import AppState, Holding, get_state

router = APIRouter(tags=["portfolio"])


@router.get("/portfolio", response_model=PortfolioResponse, operation_id="getPortfolio")
def get_portfolio(state: AppState = Depends(get_state)) -> PortfolioResponse:
    """Every held position with its symbol, quantity and average entry, plus the totals.

    `unrealised_pnl` is computed here rather than stored, so it cannot go stale between
    ticks: it is a function of the latest close, which moves every second.
    """
    positions = [_position(holding, state) for holding in state.positions.values()]
    return PortfolioResponse(positions=positions, totals=_totals(positions, state))


def _position(holding: Holding, state: AppState) -> Position:
    last = state.buffers[holding.symbol].latest().close
    return Position(
        symbol=holding.symbol,
        quantity=holding.quantity,
        avg_entry=holding.avg_entry,
        unrealised_pnl=(last - holding.avg_entry) * holding.quantity,
    )


def _totals(positions: list[Position], state: AppState) -> PortfolioTotals:
    """Value, return and today's change over the holdings, plus uninvested cash.

    Today's change is the day's move on each holding's *value*, so an instrument's day
    change percentage is applied to what is held of it rather than averaged across the
    book — a large position moving 1% matters more than a small one moving 3%.
    """
    holdings_value = 0.0
    cost = 0.0
    day_change = 0.0
    for position in positions:
        buffer = state.buffers[position.symbol]
        last = buffer.latest().close
        value = last * position.quantity
        holdings_value += value
        cost += position.avg_entry * position.quantity
        # value_now - value_at_session_start, derived from the same day change % every
        # other surface displays rather than from a second reading of the buffer.
        pct = buffer.day_change_pct()
        day_change += value - value / (1.0 + pct / 100.0)

    value = holdings_value + state.cash
    total_return = holdings_value - cost
    invested_start = value - day_change
    return PortfolioTotals(
        value=value,
        cash=state.cash,
        total_return=total_return,
        total_return_pct=(total_return / cost * 100.0) if cost else 0.0,
        day_change=day_change,
        day_change_pct=(day_change / invested_start * 100.0) if invested_start else 0.0,
    )
