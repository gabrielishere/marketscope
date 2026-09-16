"""The FastAPI application, its CORS middleware and the lifespan that runs the clock.

The frontend is cross-origin in development, so without this middleware no request
reaches the API at all.

**The clock.** The simulation advances on wall time, not on requests: the lifespan
builds the process state — which backfills 780 ticks of history — and starts one
background task that calls `advance_once` once a second for the life of the process.
The task's body is that one call and nothing else: no logging, no metrics, no
conditional work. Everything a tick does lives in `app.state.advance_once`, where a
test can call it directly, so the loop carries no behaviour of its own.

Routers are registered at the bottom, each owning its own slice of the surface.
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.routers import impact, market, movers, portfolio, scenario
from app.state import TICK_SECONDS, AppState, advance_once, get_state

#: The Angular dev server's origins. Cross-origin in dev, which is why CORS is here.
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

async def _tick_loop(state: AppState) -> None:
    """One tick a second, for as long as the process lives."""
    while True:
        await asyncio.sleep(TICK_SECONDS)
        advance_once(state)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Build the backfilled state, run the clock, and stop it on shutdown.

    The state is built before the task starts, so the first request is served against
    a full 780-tick history rather than an empty one. On shutdown the task is
    cancelled and awaited, so the loop does not outlive the application.
    """
    state = get_state()
    app.state.app_state = state
    task = asyncio.create_task(_tick_loop(state))
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


def generate_unique_id(route: APIRoute) -> str:
    """The operation id for a route: the one its decorator declares.

    FastAPI's default composes name, path and method into ids like
    `get_quotes_quotes_get`, and the generator turns those straight into the client's
    TypeScript method names. Every route here declares an explicit `operation_id`, so
    this exists to make a missing one **fail loudly** rather than fall back to a default
    that would reach the frontend as a method name nobody chose.

    Derived from the route, never from a counter or from declaration order, so the ids
    are stable across runs and adding a route does not renumber the others.
    """
    if not route.operation_id:
        raise ValueError(
            f"{route.path} declares no operation_id. Every route declares one, because "
            "the generated client takes its method names from them."
        )
    return route.operation_id


app = FastAPI(
    lifespan=lifespan,
    generate_unique_id_function=generate_unique_id,
    title="Trading demo API",
    description=(
        "Simulated market data: a fixed instrument universe advancing on a factor "
        "model, a library of world events, and a typed contract over both."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(portfolio.router)
app.include_router(movers.router)
app.include_router(scenario.router)
app.include_router(impact.router)

#: Pinned unconditionally. FastAPI emits 3.1 by default and `ng-openapi-gen` may reject
#: it — and the task that would discover the rejection is in the frontend spec, which
#: cannot fix it here. So this is pinned rather than tried.
app.openapi_version = "3.0.2"
