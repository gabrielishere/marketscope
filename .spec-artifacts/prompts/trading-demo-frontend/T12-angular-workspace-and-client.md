---
name: angular-workspace-and-client
description: Create the Angular workspace and generate the typed API client from the committed schema.
task: T12
model: claude-opus-5
---

# Objective

Create the complete Angular workspace — scaffold included — and generate the typed API client
from the emitted schema, committing the output. This is the first task in
`trading-demo-frontend`; nothing exists under `frontend/` yet.

# Outcome

`npm run gen:api` regenerates the client from `backend/openapi.json`. The generated services
cover all 12 operations. `npx ng build` succeeds with no backend process running and no file
created by a later task present.

- **Evidenced by:** `cd frontend && npm install && npm run gen:api && npx ng build` — run with
  no backend process running, output pasted. Then, from `backend/`,
  `grep -o '"operationId": "[^"]*"' openapi.json | sort -u | wc -l` — confirming it is 12.
  Then, from `frontend/`, confirm each of those 12 operation ids appears at least once under
  `src/app/api/`, output pasted. Count against the contract, not against the generator's
  output shape — a per-file `grep -c` reports one line per file, and the emitter may write
  more than one symbol per operation, so neither yields 12 on its own.
- **Deferred to human review:** none. This task's outcome is fully established by the build.

# Task context

- Anything below restated from the spec reproduces `## Definitions`, `## Visual design` and
  `## Frontend evidence` in `.spec-artifacts/specs/trading-demo-frontend.md`. **If this prompt
  and the spec disagree, the spec governs**, and the disagreement is a defect to report rather
  than one to resolve. Read that file if a term here is thinner than the work needs.
- **You have no browser.** An instruction to report what a rendered page does is one you
  cannot carry out, and you are required to say so rather than invent an observation. Every
  behavioural claim in this task is listed under *Deferred to human review* and is **not**
  yours to assert. Report it as deferred.
- **`.spec-artifacts/design/dashboard-mock.html` is the approved visual target.** It is a
  static two-route reference — no framework, no data, no polling — showing the oil-shock
  scenario active. Read it. Your component must read as its counterpart does: same ramp, same
  spacing, same type scale, same density. Where this prompt and the mockup differ on an
  appearance, the mockup governs.
- **The backend must have run.** `backend/openapi.json` is committed by the backend spec's
  T11. If it is absent, STOP and report it — do not scaffold against a guessed contract.
- The build must succeed **with no backend process running**. That is the whole reason the
  schema is a committed file rather than something fetched from a live server.
- No UI or styling package. No Angular Material, no Tailwind, no icon library, no CSS
  framework. Styling is hand-rolled and arrives in T13.
- `src/styles.css` is created here **empty** and registered in `angular.json` as the sole
  global stylesheet. T13 fills it. Creating it here is what lets T13 add the token file
  without touching build config.
- Standalone components throughout. No `NgModule`.

# Deliverables

- **CREATE** `frontend/package.json` — with a `gen:api` script and no UI or styling dependency
- **CREATE** `frontend/angular.json` — registering `src/styles.css` as the sole global stylesheet
- **CREATE** `frontend/src/styles.css` — empty
- **CREATE** `frontend/tsconfig.json`, `frontend/tsconfig.app.json`
- **CREATE** `frontend/src/index.html`
- **CREATE** `frontend/src/main.ts` — bootstraps the root standalone component
- **CREATE** `frontend/src/app/app.config.ts` — provides `HttpClient`, the API base URL and `provideRouter`
- **CREATE** `frontend/src/app/app.routes.ts` — `/` → dashboard, `/markets` → markets table
- **CREATE** `frontend/ng-openapi-gen.json`
- **CREATE** `frontend/src/app/api/` — the generated client, committed

# Instructions

1. CREATE `frontend/package.json`
2. CREATE `frontend/angular.json`
3. CREATE `frontend/tsconfig.json`
4. CREATE `frontend/ng-openapi-gen.json`
5. FOR EACH path in `src/styles.css`, `src/index.html`, `src/main.ts`, `src/app/app.config.ts`, `src/app/app.routes.ts`, `tsconfig.app.json` — CREATE it under `frontend/`
6. CREATE `frontend/src/app/api/`

# Constraints

- The routes `/` and `/markets` must both resolve at this task. Point them at placeholder
  standalone components if T13's are not yet written — a route that 404s is not a scaffold.
- The generated client is **committed**, not gitignored. The repository's `.gitignore` already
  says so deliberately.
- Do not add a test framework. None is installed and none is to be added.
- Do not write `tokens.css`, a component style or any colour. That is T13's and duplicating it
  here would give the design system two sources.
- If the generator rejects the schema, STOP and report the rejection verbatim. Do not
  hand-edit `backend/openapi.json` — it is the backend spec's deliverable.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence. Then the pasted output of the install, generate and build, the operation count, and
the per-id confirmation. Then list the 12 operation ids and, beside each, the generated
TypeScript method name it produced — later tasks call these by name and cannot ask.
