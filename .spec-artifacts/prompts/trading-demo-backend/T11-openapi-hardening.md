---
name: openapi-hardening
description: Pin the schema version, give every route an explicit operation id and tag, and emit openapi.json by importing the app.
task: T11
model: claude-opus-5
---

# Objective

Give every route an explicit operation id and a tag, pin the schema version the generator
accepts, and emit the schema to a file by importing the app, so the client generator needs no
running server. This is the last backend task and its output is what the frontend spec builds
on.

# Outcome

`backend/openapi.json` exists on disk and declares `"openapi": "3.0.2"`. All 12 operations
carry an explicit `operationId` and at least one tag. No operation id matches the FastAPI
default form `<name>_<path>_<method>`.

- **Evidenced by:** `cd backend && uv run python scripts/emit_openapi.py && uv run pytest
  tests/test_openapi.py -v` — the test reads the emitted file and asserts the version string,
  asserts the operation count is exactly 12 and reports the ids it found, asserts every
  operation has at least one tag, and asserts no id matches the default form. Run before
  replying and paste the output.

# Task context

- **The 12 operations** are: `GET /symbols`, `GET /quotes`, `GET /candles/{symbol}` (T6);
  `GET /portfolio` (T7); `GET /movers`, `GET /macro` (T8); `GET /scenarios`, `GET /scenario`,
  `POST /scenario`, `DELETE /scenario` (T9); `GET /impact/portfolio`, `GET /impact/{symbol}`
  (T10). If the emitted count is not 12, a route is missing or an extra one exists — report
  it rather than adjusting the expected number.
- **Pinning to 3.0.2 is unconditional.** FastAPI emits 3.1 by default and `ng-openapi-gen` may
  reject it. The task that would discover the rejection is in the other spec and cannot fix
  it here, which is why this is pinned rather than tried.
- **The schema is emitted by importing the app, never by running a server.** No task in this
  build depends on a live process, and no ASGI server is declared as a dependency.
- `generate_unique_id` is what replaces FastAPI's default operation ids. The default form
  produces client method names like `get_quotes_quotes_get`, which the generated TypeScript
  then carries.
- `backend/openapi.json` is committed deliberately — it is gitignored nowhere, because the
  frontend spec generates its client from the committed file with no backend running.

# Deliverables

- **UPDATE** `backend/app/main.py` — set `app.openapi_version = "3.0.2"`
- **CREATE** `backend/scripts/emit_openapi.py` — imports the app and writes the schema
- **CREATE** `backend/openapi.json` — the emitted artefact, committed
- **Function(s):** `generate_unique_id(route) -> str`
- **Evidence:** `backend/tests/test_openapi.py`

# Instructions

1. UPDATE `backend/app/main.py`
2. ADD function `generate_unique_id(route) -> str` in `backend/app/main.py`
3. CREATE `backend/scripts/emit_openapi.py`
4. CREATE `backend/tests/test_openapi.py`

# Constraints

- The emit script imports the app. It does not start a server, and it does not fetch a URL.
- Operation ids are stable across runs — derived from the route, not from a counter, a hash of
  ordering, or anything that changes when routes are added.
- Do not add, remove or rename a route in this task. If one is missing, that is a defect in
  T6–T10 to report.
- `backend/openapi.json` is a build artefact produced by running the script, not a file
  written by hand.
- If the emitted operation count is not 12, STOP and report which operation is missing or
  extra.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted output of both commands. Then list all 12 operation ids as emitted,
one per line, since the frontend spec's generated client takes its method names from them.
