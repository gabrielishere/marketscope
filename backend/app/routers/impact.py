"""What moved an instrument, and what it did to the book — in plain language first.

**Route order is load-bearing, not stylistic.** `get_portfolio_impact` is declared
*before* `get_symbol_impact`. Declared the other way round, FastAPI matches `/impact/
portfolio` against `/impact/{symbol}` and the portfolio breakdown becomes an instrument
lookup for a symbol named `portfolio`, which does not exist. That is O8, and the ordering
here is the whole of its implementation.

**Nothing is recomputed.** Every bar already carries its per-factor contributions and its
residual, written by the engine at the moment the price was derived from them. This
module sums them over a window. That is why the reconciliation holds to 1e-6 by
construction rather than by two calculations agreeing.

**The window is the scenario, or the session.** With a scenario active the window opens
at `activated_at`, so the panel answers "what did this event do". At baseline it opens at
session start, so the panel still answers something rather than going blank.

**The sentences carry no exposure value.** `oil beta -0.9` in the collapsed view is the
specific failure O18 names. `FACTOR_SENTENCES` holds phrases a non-technical reader
understands, and the exposure is served alongside for the expanded detail only.
"""

from math import log

from fastapi import APIRouter, Depends, HTTPException, status

from app.buffer import FACTORS, Bar, RingBuffer, session_start_tick
from app.models import FactorContribution, PeerImpact, PortfolioImpact, SymbolImpact
from app.state import AppState, get_state

router = APIRouter(tags=["impact"])

#: One plain-language phrase per factor, as (what a rise reads like, what a fall reads
#: like). No beta, no exposure, no factor jargon — these are read by someone who does not
#: know what a beta is, which is the whole point of the collapsed view.
FACTOR_SENTENCES: dict[str, tuple[str, str]] = {
    "market": ("the market as a whole rising", "the market as a whole falling"),
    "rates": ("interest rates rising", "interest rates falling"),
    "oil": ("the oil price rising", "the oil price falling"),
    "usd": ("a stronger dollar", "a weaker dollar"),
    "credit": ("credit conditions easing", "credit conditions tightening"),
}

#: How a contribution is introduced, by its rank among the factors and its direction.
_LEADS = {
    (0, True): "Most of the move came from",
    (0, False): "Most of the move came from",
    (1, True): "It was helped by",
    (1, False): "It was held back by",
    (2, True): "A smaller lift came from",
    (2, False): "A smaller drag came from",
}


@router.get(
    "/impact/portfolio",
    response_model=PortfolioImpact,
    operation_id="getPortfolioImpact",
)
def get_portfolio_impact(state: AppState = Depends(get_state)) -> PortfolioImpact:
    """The same decomposition, one entry per holding, plus the book's total.

    **Declared before the symbol route.** See the module docstring.
    """
    holdings = [_impact(symbol, state) for symbol in state.positions]
    total = sum(one.position_impact or 0.0 for one in holdings)
    return PortfolioImpact(holdings=holdings, total_impact=total)


@router.get(
    "/impact/{symbol}", response_model=SymbolImpact, operation_id="getSymbolImpact"
)
def get_symbol_impact(
    symbol: str, state: AppState = Depends(get_state)
) -> SymbolImpact:
    """The move since the window opened, what drove it, and same-sector peers."""
    if symbol not in state.instruments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown symbol: {symbol!r}."
        )
    return _impact(symbol, state)


def _window(buffer: RingBuffer, activated_at: int | None) -> tuple[Bar, ...]:
    """The bars the decomposition covers: since activation, or since session start."""
    bars = buffer.bars()
    if not bars:
        return ()
    start = activated_at if activated_at is not None else session_start_tick(bars[-1].t)
    return tuple(bar for bar in bars if bar.t >= start)


def _impact(symbol: str, state: AppState) -> SymbolImpact:
    buffer = state.buffers[symbol]
    instrument = state.instruments[symbol]
    window = _window(buffer, state.activated_at)

    if not window:
        return SymbolImpact(
            symbol=symbol, move_pct=0.0, log_return=0.0, contributions=[],
            residual=0.0, position_impact=None, peers=[],
        )

    opening = window[0].open
    closing = window[-1].close
    # The stored attribution *is* the return: each bar's price was derived from these
    # numbers, so summing them over the window reconciles with the window's log return
    # by construction.
    totals = {
        factor: sum(bar.contributions[factor] for bar in window) for factor in FACTORS
    }
    residual = sum(bar.residual for bar in window)

    ordered = sorted(totals.items(), key=lambda item: abs(item[1]), reverse=True)
    contributions = [
        FactorContribution(
            factor=factor,
            exposure=instrument.betas[factor],
            factor_move_pct=_factor_move_pct(factor, instrument.betas[factor], value),
            contribution=value,
            sentence=_sentence(rank, factor, value),
        )
        for rank, (factor, value) in enumerate(ordered)
    ]

    holding = state.positions.get(symbol)
    return SymbolImpact(
        symbol=symbol,
        move_pct=(closing / opening - 1.0) * 100.0,
        log_return=log(closing / opening),
        contributions=contributions,
        residual=residual,
        position_impact=(
            holding.quantity * (closing - opening) if holding is not None else None
        ),
        peers=_peers(symbol, state),
    )


def _factor_move_pct(factor: str, exposure: float, contribution: float) -> float:
    """The factor's own move, recovered from the contribution and the exposure.

    Zero exposure means the factor moved but this instrument did not follow it, and the
    contribution carries no information about the factor's own move — so it reads 0.0
    rather than a division by zero.
    """
    if exposure == 0.0:
        return 0.0
    return (pow(2.718281828459045, contribution / exposure) - 1.0) * 100.0


def _sentence(rank: int, factor: str, contribution: float) -> str:
    """One plain-language sentence, carrying no beta and no exposure value."""
    rose, fell = FACTOR_SENTENCES[factor]
    # The phrase describes the factor's own direction; the lead says what that did to
    # this instrument. A negative exposure means a rising factor hurt it, and the two
    # halves carry that without naming a beta.
    phrase = rose if contribution >= 0 else fell
    lead = _LEADS.get((rank, contribution >= 0))
    if lead is None:
        return f"{phrase.capitalize()} played a small part."
    return f"{lead} {phrase}."


def _peers(symbol: str, state: AppState) -> list[PeerImpact]:
    """Same-sector instruments, ranked by descending absolute move over the window.

    A field rather than a second request: the impact panel ranks peers by impact, and
    without this it would issue one `/impact/{symbol}` call per instrument in the sector.
    """
    sector = state.instruments[symbol].sector
    peers = []
    for other, instrument in state.instruments.items():
        if other == symbol or instrument.sector != sector:
            continue
        window = _window(state.buffers[other], state.activated_at)
        if not window:
            continue
        move = (window[-1].close / window[0].open - 1.0) * 100.0
        peers.append(PeerImpact(symbol=other, name=instrument.name, move_pct=move))
    return sorted(peers, key=lambda peer: abs(peer.move_pct), reverse=True)
