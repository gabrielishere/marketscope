"""The FastAPI application and its CORS middleware.

The frontend is cross-origin in development, so without this middleware no request
reaches the API at all.

This module declares no route. Routers arrive in T6-T10.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#: The Angular dev server's origins. Cross-origin in dev, which is why CORS is here.
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app = FastAPI(
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
