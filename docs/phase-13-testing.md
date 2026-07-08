# Phase 13 — Testing

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete.
**Depends on:** Phases 1–12.

> Every prior phase already shipped unit tests (fakes/mocks against use
> cases) and was manually verified live. Phase 13's job is what was still
> missing: a real, checked-in **integration** suite (API + real Postgres +
> real S3-compatible storage, no mocks at the wiring layer) and a real,
> checked-in **E2E** suite (headless Chromium driving the actual UI against
> the actual backend) — both runnable on demand instead of being one-off
> verification scripts, plus a coverage baseline.

## Backend integration tests (`tests/integration/`, 17 tests)

- **Why a separate suite from the 52 existing unit tests**: unit tests
  exercise use cases against in-memory fakes — fast, but they never touch
  SQLAlchemy models, real SQL, Alembic migrations, the FastAPI dependency
  graph, or a real S3-compatible upload/download round trip. Integration
  tests do, catching exactly the class of bug unit tests structurally can't
  (see Errors below — this suite caught two).
- **Infrastructure**: a dedicated `verify_test` Postgres database (separate
  from the `verify` dev database used for manual verification), the same
  local Redis, and the same moto S3 mock already used throughout this
  project. `tests/conftest.py` sets `DATABASE_URL`/`REDIS_URL`/`S3_*` env
  vars at import time (before any `app.*` import can cache stale settings
  via `get_settings()`'s `lru_cache`), so the suite doesn't depend on
  external environment setup beyond having those services reachable.
- **`tests/integration/conftest.py`**: runs `alembic upgrade head` against
  `verify_test` once per session; a `client` fixture builds the real FastAPI
  app per test (full `lifespan`, so bucket-ensure and engine
  creation/disposal run for real) with only the Celery **dispatch port**
  overridden to a `FakePipelineDispatcher` — tests assert the pipeline was
  *enqueued*, not that it *ran* (running it is Phase 9-12's manual-E2E
  territory and would make this suite depend on a live worker); a
  `db_session` fixture and `_truncate_after_test` autouse fixture give tests
  direct DB access for setup/assertions and guarantee isolation between
  tests; `seed_staff_user`/`mark_pending_review` helpers stand in for the
  two things this suite deliberately doesn't run for real (out-of-band
  officer provisioning, and pipeline-driven status transitions).
- **Coverage**: full auth lifecycle (register/login/refresh/rotation/me,
  and a regression guard that self-registration can never grant an elevated
  role); the application lifecycle (create → presigned upload ×3 → confirm →
  submit, missing-artifact rejection, cross-applicant 404 isolation);
  officer review (evidence view, empty-reason 422, approve, re-decide 409,
  audit trail, role matrix — officer decides, auditor reads-only, applicant
  denied); reports & analytics (all three formats generated and downloaded
  through real presigned URLs, bulk export PDF-rejection and multi
  -application coverage, analytics aggregates checked against directly
  -seeded data, staff-only gating).

## Frontend E2E tests (`frontend/e2e/`, Playwright, 6 tests)

- `playwright.config.ts` targets the pre-installed Chromium
  (`/opt/pw-browsers/chromium`) and deliberately does **not** start any
  service itself (`webServer` left unset) — orchestrating the full stack
  end-to-end is Phase 14's job; until then this mirrors exactly how this
  project's manual verification has worked since Phase 8: start
  Postgres/Redis/moto/backend/Celery/frontend, then run the suite against
  them.
- `e2e/support.ts` does test **setup** (register users, create/upload
  /submit applications) via direct `fetch` calls to the backend rather than
  driving the browser for it — the same "make it fast" principle from
  Phase 11's live-verification lesson, now baked into the checked-in suite
  instead of being an ad hoc script.
- **Specs**: `auth.spec.ts` (register → dashboard, duplicate email, wrong
  password), `application-upload.spec.ts` (real create-application form,
  real hidden-file-input uploads via `setInputFiles`, submit), `officer
  -review.spec.ts` (waits for the **real, live** AI pipeline to reach
  `pending_review`, then drives the actual review UI: evidence pack render,
  reviewed-checkbox gate, approve, and the Phase-12 report button opening a
  real generated PDF in a new tab), `analytics.spec.ts` (live KPI dashboard
  render, bulk CSV export via the browser's download event).

## Coverage baseline

- Added `pytest-cov`; `[tool.coverage.report]` in `pyproject.toml` sets
  `fail_under = 85`, a little below the measured 90% branch coverage
  (89.82%) so the gate catches real regressions without being brittle
  against any single untested branch.
- Deleted `app/core/container.py` — a Phase-6 scaffold composition root that
  was fully superseded by the per-feature `interfaces/api/v1/deps/*.py`
  modules from Phase 7 onward and had zero references left in the codebase;
  coverage tooling surfaced it as 0%-covered dead code.

## Errors and fixes (found by the new tests, not by design)

1. **Stale sessionmaker across event loops** — `app/infrastructure/db
   /session.py`'s `dispose_engine()` reset the module-global `_engine` but
   not `_sessionmaker`. Harmless in production (the function only ever runs
   once, at real process shutdown), but the integration suite's
   per-test-fresh-app pattern (each test's `lifespan` disposes the engine at
   teardown) exposed it immediately: the next test's app would get a
   sessionmaker still bound to a disposed engine from a *different* asyncio
   event loop, crashing every DB call after the first test with `asyncpg
   ... attached to a different loop`. Fixed by also clearing `_sessionmaker`
   in `dispose_engine()` — a real bug fix, not a test-only workaround, since
   any process that tears down and re-initializes the DB layer more than
   once (this test harness now; conceivably a future worker-recycling
   scheme) would hit the same crash.
2. **Local Postgres cluster initialized as `SQL_ASCII`, not `UTF8`** —
   surfaced when `officer-review.spec.ts` (E2E) submitted a decision reason
   containing an em-dash and the backend threw `asyncpg
   .UntranslatableCharacterError`. Root cause: this sandbox's `initdb` had
   defaulted to `SQL_ASCII` for the whole cluster (`template0`/`template1`
   included), which every database created from it inherits. This is not a
   theoretical edge case for this app — its own currency formatting emits
   `₹` everywhere (application details, reports, bulk exports), so **any**
   real Indian Rupee amount would have crashed decision-recording, report
   generation, and probably more, in this environment. Fixed by dropping and
   recreating both `verify` and `verify_test` with `ENCODING 'UTF8' TEMPLATE
   template0`, then re-running migrations. Added a permanent regression
   guard: `test_officer_can_view_evidence_and_record_a_decision` now submits
   a decision reason containing accented characters, an em-dash, and a `₹`
   amount, and asserts it round-trips exactly. (The official `postgres`
   Docker image Phase 14 will use defaults to UTF8, so this specific failure
   mode is a sandbox artifact — but the regression test guards the
   application-level behavior regardless of what created the database.)

## Verification performed

- `pytest --cov=app` — **69 passed** (52 unit + 17 integration), 90% branch
  coverage, `fail_under = 85` gate passes.
- `ruff check app tests` and `mypy app tests --strict` — clean (166 source
  files).
- Migration parity re-confirmed clean after all changes (an autogenerate
  check produces an empty upgrade/downgrade).
- `npx tsc --noEmit` and `next build` — clean, including the new `e2e/*.ts`
  and `playwright.config.ts` files.
- Full live stack (Postgres, Redis, moto S3, one Celery worker, backend,
  frontend) brought up fresh after the database re-creation; `npx
  playwright test` — **6/6 passed**, including the officer-review spec
  waiting on the real pipeline and generating a real PDF report.

## Notes & deferrals

- The E2E suite's `officer-review.spec.ts` depends on a live Celery worker
  actually finishing the AI pipeline (`waitForPendingReview` polls for up to
  60s) — by design, matching how this project has always verified the
  pipeline, but it means this one spec is slower and has an external
  dependency the other five don't. Phase 14 (Docker Compose) is the natural
  place to make "the full stack is up" a one-command precondition instead of
  a manually-followed runbook.
- No CI workflow file yet (e.g. GitHub Actions) — running these suites is
  still a manual/local-orchestration step. Wiring them into CI is deferred
  to Phase 14/15 once the Docker Compose stack gives CI a
  one-command way to stand up Postgres/Redis/MinIO/a worker.
- Coverage gate is process-level (`fail_under` on the whole `app/` tree), not
  per-file — a few infrastructure modules that need a live Celery worker or
  broker to exercise meaningfully (`celery_app.py`, `pipeline_tasks.py`) are
  at 0% and intentionally not chased, since faking Celery's own decorator
  machinery would test the fake, not the code.
