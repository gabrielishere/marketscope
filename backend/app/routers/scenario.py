"""The scenario library, the active scenario, and its activation and deletion.

This is the surface the whole demo is driven from: a presenter picks a world event here
and the market changes underneath them.

**Activation never rewrites history.** `Engine.activate` records the tick index of the
*next* bar to be written and changes nothing already in the buffers. Bars are appended
and never revisited, so every bar before `activated_at` is byte-identical afterwards. If
it were otherwise the chart would visibly redraw its own past mid-demo, which an audience
notices immediately.

**An unknown id is a 422, not a 500.** `ScenarioId` is generated from the JSON and
declared on the request body, so FastAPI rejects an id outside the library before the
handler runs.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.models import ActiveScenario, ScenarioSummary
from app.scenarios import Scenario, ScenarioId, load_scenarios
from app.state import AppState, advance_once, get_state

router = APIRouter(tags=["scenario"])


class ActivateScenarioRequest(BaseModel):
    """The body of `POST /scenario`. Typed to the enum, which is what makes a 422."""

    id: ScenarioId = Field(description="An id the scenario library holds.")


@router.get(
    "/scenarios", response_model=list[ScenarioSummary], operation_id="listScenarios"
)
def get_scenarios() -> list[ScenarioSummary]:
    """The library, in file order, which places the baseline first."""
    return [
        ScenarioSummary(id=scenario.id, name=scenario.name, description=scenario.description)
        for scenario in load_scenarios().values()
    ]


@router.get("/scenario", response_model=ActiveScenario, operation_id="getActiveScenario")
def get_scenario(state: AppState = Depends(get_state)) -> ActiveScenario:
    """The active scenario, its headlines, and the tick it was activated at.

    `activated_at` is null at baseline. The headlines are served from here rather than
    held in the client, so a scenario change reaches the ticker without a redeploy.
    """
    return _active(state.scenario, state.activated_at)


@router.post("/scenario", response_model=ActiveScenario, operation_id="activateScenario")
def post_scenario(
    request: ActivateScenarioRequest, state: AppState = Depends(get_state)
) -> ActiveScenario:
    """Make a scenario active, apply it, and report the state that results.

    **The tick is the point.** `activate()` stamps the index of the next bar to be written;
    the shock does not exist until that bar exists. Returning before writing it would report
    success while every price is still the old one, and a client refreshing immediately —
    which is exactly what the selector does — would fetch stale quotes and show nothing
    happening until the next scheduled poll, up to three and a half seconds later.

    So this endpoint makes the change real before it says it is done.
    """
    scenario = load_scenarios()[request.id]
    state.engine.activate(scenario)
    advance_once(state)
    return _active(state.scenario, state.activated_at)


@router.delete(
    "/scenario", response_model=ActiveScenario, operation_id="deactivateScenario"
)
def delete_scenario(state: AppState = Depends(get_state)) -> ActiveScenario:
    """Return to baseline, clearing `activated_at`.

    The bars written while the scenario was active stay exactly as they are — going back
    to normal is a change to what happens next, not an undo.

    Ticks once before returning, for the same reason `POST` does: the unwind of the outgoing
    shock lands in the next bar, and without writing it here the client would refresh onto
    prices that have not moved yet.
    """
    state.engine.deactivate()
    advance_once(state)
    return _active(state.scenario, state.activated_at)


def _active(scenario: Scenario, activated_at: int | None) -> ActiveScenario:
    return ActiveScenario(
        id=scenario.id,
        name=scenario.name,
        headlines=list(scenario.headlines),
        activated_at=activated_at,
    )
