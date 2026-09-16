# Marketscope — one image, one service.
#
# FastAPI serves the API and the built Angular application on the same origin, so there is
# one URL to share, one service to keep awake, and no CORS in production.
#
# Two stages: Node builds the frontend, Python runs the API with that build copied in. The
# Node toolchain does not survive into the final image.
#
#   docker build -t marketscope .
#   docker run -p 8000:8000 marketscope

# ── Stage 1: build the frontend ──────────────────────────────────────────────
FROM node:22-slim AS frontend

WORKDIR /build

# Dependencies first, so a source-only change does not reinstall them.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# The generated API client is committed, so `gen:api` does not run here. That is the whole
# reason it is committed rather than ignored: this build needs no backend and no schema step.
RUN npx ng build


# ── Stage 2: run the API, serving that build ─────────────────────────────────
FROM python:3.12-slim AS runtime

# uv, for the same dependency resolution the project uses locally.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Dependencies first, again for layer caching.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

COPY backend/app ./app
COPY backend/openapi.json ./openapi.json

# Where `app.main` looks for the frontend. Absent in development, present here, which is why
# the mount is conditional rather than assumed.
COPY --from=frontend /build/dist/trading-demo/browser ./static

ENV PATH="/app/.venv/bin:$PATH"

# Render and most hosts supply $PORT; 8000 is the local default.
ENV PORT=8000
EXPOSE 8000

# One worker, deliberately. The simulation lives in this process — two workers would each
# hold their own market and serve different prices to different people.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
