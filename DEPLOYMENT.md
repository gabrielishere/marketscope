# Deployment plan

**Goal:** a reviewer reads the code and sees it running, with the least setup that achieves
both.

**Shape:** one service. FastAPI serves the built Angular app at `/` and the API on the same
origin. The frontend is *not* deployed separately — it ships inside the same container as
static files.

Two links for the reviewer: the repository for the code, one URL for the running app.

---

## Why one service rather than two

- **No CORS.** Same origin, so the cross-origin configuration the local setup needs
  disappears entirely in production.
- **One deploy, one URL, one thing to keep awake.** A frontend on a static host plus a
  backend elsewhere is two free tiers, two cold starts and a base-URL to keep in step.
- **The API is already the only stateful part.** The simulation ticks in process once a
  second; there is no database, so there is nothing else to provision.

---

## Steps

### 1. Serve the frontend from FastAPI — **done**

Mount the built Angular output as static files, after the routers so no API path is
shadowed, with an SPA fallback so a deep link to `/markets` returns `index.html` rather than
a 404.

```python
# app/main.py, after the routers are included
app.mount("/", SPAStaticFiles(directory="static", html=True), name="app")
```

The frontend's base URL now resolves at runtime: empty when served from any origin but the
dev server's port 4200, `http://localhost:8000` when `ng serve` is running. Decided by
looking at the port rather than by a build flag, because a build configuration is a second
thing to get right and this has one correct answer in each case.

### 2. Dockerfile — **done**

Two stages:

1. **Node** — `npm ci`, `npx ng build`, producing `dist/trading-demo/browser`.
2. **Python** — `uv sync`, copy `backend/`, copy the built browser output from stage 1 into
   `backend/static/`, run `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

`openapi.json` is committed, so the client generation step does **not** run in the image —
the generated client is already in the repository, which is the whole reason it is committed
rather than ignored.

### 3. Push and connect — *yours*

Push to GitHub, create a Render web service from the repo, pick "Docker". No other
configuration; Render supplies `$PORT`.

Railway and Fly.io work the same way from the same Dockerfile if Render is not the right
home.

---

## Effort

| Step | Whose | State |
|---|---|---|
| 1 — static mount and base URL | mine | done, verified locally |
| 2 — Dockerfile | mine | written, **not built** — no Docker on the authoring machine |
| 3 — push and connect | yours | mostly clicking |

**Step 2 is unverified and that matters.** The image has never been built, so the first real
test of it is Render's build. Reviewing it cold did catch one defect before it shipped —
`uvicorn` was a dev dependency while the image installs with `--no-dev`, so the container
would have built cleanly and then failed to start. It is a runtime dependency now. Others of
that shape may remain.

---

## Known limits

- **Render's free tier sleeps after ~15 minutes idle** and takes ~30 seconds to wake. Fine
  for a reviewer clicking a link. **Not** fine for presenting live — run it locally for
  that, as now.
- **State is in process and dies with it.** A restart re-runs the 780-tick backfill from the
  fixed seed, so the market comes back deterministic but the active scenario resets to
  baseline. Nothing to migrate, nothing to lose.
- **One instance only.** Two replicas would each hold their own simulation and serve
  different prices to different users. If this ever needs to scale, the state has to move
  out of the process, which is a different system — see the constraint in both specs that
  nothing is abstracted in anticipation of a persistence layer.

---

## Alternative, if the reviewer wants to run it rather than just see it

**GitHub Codespaces** puts them in a browser IDE with the repository and a forwarded port,
so reading and running happen in one place. Costs nothing to prepare — it works on any
repository — and is worth mentioning to a technical reviewer even if the deployed URL is the
main route in.

---

## What the reviewer should be pointed at

The running app is the smaller half. `.spec-artifacts/` carries the part that is actually
unusual:

- `specs/` — the two specifications the build was driven from
- `prompts/` — a prompt per task, twenty-four of them
- `decisions/` — four ADRs
- `incidents/` — two incident records, including what the method caught and what it missed
- `process/` — why the frontend was built without the gate, and what that cost
- `logs/` — twelve run records from the backend build
- `design/dashboard-mock.html` — the visual target, approved before any code was written
