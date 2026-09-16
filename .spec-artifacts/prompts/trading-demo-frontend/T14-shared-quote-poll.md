---
name: shared-quote-poll
description: The single QuoteService polling every symbol on one interval, with selection and a forced refresh.
task: T14
model: claude-opus-5
---

# Objective

Build the single `QuoteService` that polls every symbol in the universe on one RxJS interval
and lets subscribers select from the result, and expose a method to force an immediate
refresh. Every component that shows a price reads through this service.

# Outcome

One `/quotes` request goes out per interval regardless of how many components are mounted or
which route is showing. `quotes$(symbols)` returns a selection over that one stream and issues
no request of its own. `refreshNow()` issues a request without waiting out the interval.

- **Evidenced by:** `cd frontend && npx ng build`, output pasted. Then paste
  `quote.service.ts` in full and name the operator that multicasts the stream. **Exactly one
  `interval` may appear in the file**, and `quotes$` must derive from `allQuotes$()` rather
  than call the API. A second `interval`, or an API call inside `quotes$`, is the defect this
  evidence exists to expose.
- **Deferred to human review:** with the watchlist and the detail view both open, the network
  panel shows one `/quotes` request per interval, not two; and selecting a scenario produces a
  `/quotes` request sooner than the interval.

# Task context

- Anything below restated from the spec reproduces `## Definitions`, `## Visual design` and
  `## Frontend evidence` in `.spec-artifacts/specs/trading-demo-frontend.md`. **If this prompt
  and the spec disagree, the spec governs**, and the disagreement is a defect to report rather
  than one to resolve. Read that file if a term here is thinner than the work needs.
- **You have no browser.** An instruction to report what a rendered page does is one you
  cannot carry out, and you are required to say so rather than invent an observation. Every
  behavioural claim in this task is listed under *Deferred to human review* and is **not**
  yours to assert. Report it as deferred.
- **`.spec-artifacts/design/dashboard-mock.html` is the approved visual target.** Read it and
  find your component in it. Yours must read as its counterpart does: same ramp, same spacing,
  same type scale, same density. Where this prompt and the mockup differ on an appearance, the
  mockup governs.
- Every value is a `var(--token)` reference from `frontend/src/styles/tokens.css`. No raw hex,
  `px` or `ms` appears in a component — O23 is evidenced by a grep over `src/app`.
- Figures render through `frontend/src/app/core/format.ts` in a `tabular-nums` face. Never
  format a number inline; never let a column's width depend on its value.
- **It polls the universe, not each subscriber's list.** The dashboard wants a handful and the
  markets table wants all forty. A service that polls per subscriber set satisfies "one
  request per subscriber" and still issues two — which is the defect the outcome is worded to
  catch.
- The poll interval is 2–3 seconds. Pick a value in that range and name it as a constant.
- The multicast is what makes the count independent of subscriber count. A cold observable
  handed to two components issues two requests.
- `refreshNow()` exists because a scenario selection must show in the data immediately. A
  three-second wait after clicking reads as a broken demo.

# Deliverables

- **CREATE** `frontend/src/app/core/quote.service.ts`
- **Function(s):** `allQuotes$()` — the single polled stream over every symbol;
  `quotes$(symbols: string[])` — a selection over `allQuotes$()`, never a new request;
  `refreshNow()` — issues a request without waiting out the interval

# Instructions

1. CREATE `frontend/src/app/core/quote.service.ts`
2. ADD class `QuoteService` in `frontend/src/app/core/quote.service.ts`
3. ADD function `allQuotes$()` in `frontend/src/app/core/quote.service.ts`
4. ADD function `quotes$(symbols: string[])` in `frontend/src/app/core/quote.service.ts`
5. ADD function `refreshNow()` in `frontend/src/app/core/quote.service.ts`

# Constraints

- Exactly one `interval` in the file. If you need a second timer, you have the design wrong.
- `quotes$` filters the shared stream. It never calls the generated client.
- The symbol list for the poll comes from one `GET /symbols` at startup, not from each
  subscriber.
- The service is `providedIn: 'root'`, so there is one instance for the application.
- No component may be edited by this task.

# Response format

One line per deliverable, done or not done. Then one line per outcome clause with its
evidence, and the deferred items reported as deferred. Then the build output,
`quote.service.ts` in full, the name of the multicasting operator, and the chosen interval
value in milliseconds.
