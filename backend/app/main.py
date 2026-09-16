"""The FastAPI application, its CORS middleware and the lifespan that runs the clock.

The frontend is cross-origin in development, so without this middleware no request
reaches the API at all.

**The clock.** The simulation advances on wall time, not on requests: the lifespan
builds the process state — which backfills 780 ticks of history — and starts one
background task that calls `advance_once` once a second for the life of the process.
The task's body is that one call and nothing else: no logging, no metrics, no
conditional work. Everything a tick does lives in `app.state.advance_once`, where a
test can call it directly, so the loop carries no behaviour of its own.

This module declares no route. Routers arrive in T6-T10.
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


app = FastAPI(
    lifespan=lifespan,
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
