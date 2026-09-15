"""Each of the fourteen response models rejects a payload with a required field removed.

Every payload below is a literal. One case per model: the whole payload must validate,
and the same payload with the named field removed must be rejected with that field named
in the error — both sides of the boundary, so a model whose field was made optional fails
here rather than reaching the generated client as an absent key.

The field chosen for removal is, where one exists, a field whose requiredness is not
obvious: `activated_at` and `position_impact` are nullable but have no default, so they
are required and always present in the payload with `null` as a permitted value.
"""

import pytest
from pydantic import BaseModel, ValidationError

from app.models import (
    ActiveScenario,
    Candle,
    FactorContribution,
    MacroDriver,
    Mover,
    MoversResponse,
    PortfolioImpact,
    PortfolioResponse,
    PortfolioTotals,
    Position,
    Quote,
    ScenarioSummary,
    SymbolImpact,
    SymbolMatch,
)

QUOTE: dict[str, object] = {
    "symbol": "XOM",
    "last": 118.42,
    "day_change_pct": 6.18,
    "sparkline": [111.2, 113.7, 116.0, 118.42],
}

CANDLE: dict[str, object] = {
    "t": 780,
    "open": 117.9,
    "high": 118.6,
    "low": 117.4,
    "close": 118.42,
    "volume": 24100.0,
}

SYMBOL_MATCH: dict[str, object] = {
    "symbol": "XOM",
    "name": "Exxon Mobil",
    "sector": "Energy",
    "currency": "USD",
    "decimals": 2,
}

POSITION: dict[str, object] = {
    "symbol": "XOM",
    "quantity": 12.5,
    "avg_entry": 101.4,
    "unrealised_pnl": 212.75,
}

PORTFOLIO_TOTALS: dict[str, object] = {
    "value": 248310.44,
    "cash": 12480.0,
    "total_return": 18204.1,
    "total_return_pct": 7.91,
    "day_change": 3891.2,
    "day_change_pct": 1.59,
}

PORTFOLIO_RESPONSE: dict[str, object] = {
    "positions": [POSITION],
    "totals": PORTFOLIO_TOTALS,
}

MOVER: dict[str, object] = {
    "symbol": "OXY",
    "last": 71.2,
    "day_change_pct": 7.44,
    "session_volume": 1640000.0,
}

MOVERS_RESPONSE: dict[str, object] = {
    "gainers": [MOVER],
    "losers": [],
    "most_active": [MOVER],
}

MACRO_DRIVER: dict[str, object] = {
    "symbol": "WTI",
    "name": "WTI Crude",
    "factor": "oil",
    "last": 94.6,
    "day_change_pct": 9.12,
}

SCENARIO_SUMMARY: dict[str, object] = {
    "id": "oil-supply-shock",
    "name": "Oil supply shock",
    "description": "A pipeline outage cuts supply and the oil factor spikes.",
}

ACTIVE_SCENARIO: dict[str, object] = {
    "id": "oil-supply-shock",
    "name": "Oil supply shock",
    "headlines": [
        "Brent jumps 9% as pipeline outage cuts supply",
        "Airlines slide on fuel cost fears",
    ],
    "activated_at": 812,
}

FACTOR_CONTRIBUTION: dict[str, object] = {
    "factor": "oil",
    "exposure": 1.0,
    "factor_move_pct": 9.12,
    "contribution": 0.0524,
    "sentence": "The oil price rose sharply.",
}

SYMBOL_IMPACT: dict[str, object] = {
    "symbol": "XOM",
    "move_pct": 6.18,
    "log_return": 0.0599,
    "contributions": [FACTOR_CONTRIBUTION],
    "residual": 0.0075,
    "position_impact": 212.75,
}

PORTFOLIO_IMPACT: dict[str, object] = {
    "holdings": [SYMBOL_IMPACT],
    "total_impact": 1840.6,
}

# (model, complete payload, the required field removed)
CASES: list[tuple[type[BaseModel], dict[str, object], str]] = [
    (Quote, QUOTE, "day_change_pct"),
    (Candle, CANDLE, "close"),
    (SymbolMatch, SYMBOL_MATCH, "decimals"),
    (Position, POSITION, "quantity"),
    (PortfolioTotals, PORTFOLIO_TOTALS, "day_change_pct"),
    (PortfolioResponse, PORTFOLIO_RESPONSE, "totals"),
    (Mover, MOVER, "session_volume"),
    (MoversResponse, MOVERS_RESPONSE, "most_active"),
    (MacroDriver, MACRO_DRIVER, "factor"),
    (ScenarioSummary, SCENARIO_SUMMARY, "description"),
    (ActiveScenario, ACTIVE_SCENARIO, "activated_at"),
    (FactorContribution, FACTOR_CONTRIBUTION, "sentence"),
    (SymbolImpact, SYMBOL_IMPACT, "position_impact"),
    (PortfolioImpact, PORTFOLIO_IMPACT, "holdings"),
]


def test_every_named_model_has_a_case() -> None:
    """Fourteen models are named by the task; fourteen cases cover them."""
    assert len(CASES) == 14
    assert len({model for model, _, _ in CASES}) == 14


@pytest.mark.parametrize(
    ("model", "payload", "removed"),
    CASES,
    ids=[model.__name__ for model, _, _ in CASES],
)
def test_model_rejects_payload_with_required_field_removed(
    model: type[BaseModel], payload: dict[str, object], removed: str
) -> None:
    # The complete payload validates — without this the rejection below proves nothing.
    model.model_validate(payload)

    incomplete = {key: value for key, value in payload.items() if key != removed}
    assert removed not in incomplete
    assert len(incomplete) == len(payload) - 1

    with pytest.raises(ValidationError) as excinfo:
        model.model_validate(incomplete)

    missing = [
        error["loc"][0] for error in excinfo.value.errors() if error["type"] == "missing"
    ]
    assert removed in missing


@pytest.mark.parametrize(
    ("model", "payload", "field"),
    [
        (ActiveScenario, ACTIVE_SCENARIO, "activated_at"),
        (SymbolImpact, SYMBOL_IMPACT, "position_impact"),
    ],
    ids=["ActiveScenario.activated_at", "SymbolImpact.position_impact"],
)
def test_nullable_required_field_accepts_null(
    model: type[BaseModel], payload: dict[str, object], field: str
) -> None:
    """Required but nullable: the key is always present, `null` is a permitted value."""
    validated = model.model_validate({**payload, field: None})

    assert getattr(validated, field) is None
