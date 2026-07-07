# Phase 6 — Backend Initialization

**Project:** AI Co-Applicant Verification Platform (`loan-verification-ai`)
**Status:** Complete — migrates, boots, and serves against live Postgres + Redis.
**Depends on:** Phases 1–5.

> Stands up the FastAPI backend skeleton in the clean-architecture layering
> from Phase 2, with the full Phase-3 database schema as SQLAlchemy models, a
> reviewed Alembic migration, async DB access, structured logging, health
> probes, and the versioned `/api/v1` OpenAPI surface.

## What shipped

**Project & tooling**
- `pyproject.toml` — FastAPI, SQLAlchemy 2 (async, asyncpg), Alembic, Redis,
  pydantic-settings, python-jose, passlib[argon2]; dev extras (pytest,
  httpx, ruff, mypy). Ruff + strict mypy configured.

**Core** (`app/core/`)
- `config.py` — `pydantic-settings` with validated env, comma-separated CORS
  parsing, and a derived synchronous DSN for Alembic.
- `logging.py` — structured JSON logs carrying the request correlation id.
- `container.py` — the composition root (DI); binds ports to infrastructure.

**Domain** (`app/domain/`)
- `value_objects/enums.py` — all 12 closed value sets as `StrEnum`, the single
  source for both the domain and the persisted PostgreSQL ENUM types.
- `exceptions/` — framework-agnostic domain error hierarchy mapped to HTTP
  status codes by a single handler.

**Infrastructure** (`app/infrastructure/`)
- `db/base.py` — declarative base with a constraint-naming convention (stable,
  reviewable migrations) and UUID / timestamp / created-at mixins.
- `db/models/` — **all 13 tables** from Phase 3 with UUID PKs, FKs and their
  delete semantics, CHECK constraints, and partial indexes (officer queue,
  current risk score, singleton artifacts, unread notifications).
- `db/session.py` — lazy async engine + request-scoped session dependency.
- `db/migrations/` — Alembic wired to app settings and model metadata; the
  reviewed initial migration creates `citext`/`pgcrypto` and tears down enum
  types on downgrade.
- `health/checks.py` — real DB and Redis reachability checks.

**Interfaces** (`app/interfaces/`)
- `middleware/` — request-id (ContextVar-backed, echoed on responses) and a
  centralized domain-error / unhandled-exception JSON envelope.
- `api/v1/` — health (`/health`) and readiness (`/ready`) routers, Pydantic
  schemas, aggregate router mounted under `/api/v1`.
- `main.py` — application factory with lifespan management and middleware
  ordering (request-id outermost).

## Verification performed (against a live PostgreSQL 16 + Redis)

- `alembic upgrade head` — succeeds; creates 13 tables, 13 ENUM types, and all
  partial indexes.
- **Reversibility** — `alembic downgrade base` cleanly drops every table *and*
  enum type (back to just `alembic_version`), then `upgrade head` again.
- **Model/migration parity** — `alembic revision --autogenerate` detects **no
  changes**, proving the models and the migration are in exact agreement.
- **Live app** — `uvicorn` boots; `/api/v1/health` returns ok, `/api/v1/ready`
  returns `database: true, redis: true` against real connections; the
  `X-Request-ID` header is stamped; OpenAPI generates with the correct title,
  version, and paths.
- **Quality gates** — `ruff` clean, `mypy` strict clean (58 files), `pytest`
  green (config, model-registration/DDL-compile, and liveness API tests).

## Deliberately deferred (to their proper phases)

- Auth endpoints + JWT/refresh logic and RBAC dependencies → Phase 7.
- Repositories, use cases, and feature routers (applications, uploads,
  officer, reports, audit) → Phases 7–12.
- Seed migration for the initial admin user and active `risk_engine_config`
  → alongside auth (Phase 7) / Docker (Phase 14).
- Full integration test suite against ephemeral Postgres → Phase 13.
