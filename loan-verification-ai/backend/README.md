# backend/ — FastAPI service (Clean Architecture)

REST API, authentication, orchestration of the AI pipeline, and all database
access. Dependency rule is strict: **arrows point inward**; `domain/` has zero
third-party imports.

```
app/
  domain/            # entities, value objects (incl. enums), domain services, exceptions
  application/       # use cases + ports (interfaces the domain needs from outside)
    ports/           #   repositories/ and services/ — abstract interfaces
    use_cases/       #   one class per business operation
    dto/             #   framework-independent data objects
  infrastructure/    # implements application/ports — the ONLY layer with 3rd-party imports
    db/              #   SQLAlchemy models, session, Alembic migrations
    storage/ ai/ tasks/ auth/ notifications/ health/
  interfaces/        # outermost — HTTP presentation
    api/v1/          #   routers/, schemas/ (Pydantic), deps/
    middleware/      #   request-id, error handling
  core/              # config (pydantic-settings), DI container, logging
tests/               # unit / integration / api
```

## Local development

Prerequisites: Python 3.11+, PostgreSQL 14+, Redis. (Or use the project's
`docker compose` in Phase 14, which provisions both.)

```bash
# 1. Install (editable, with dev extras)
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # or: uv pip install -e ".[dev]"

# 2. Configure
cp .env.example .env             # edit DATABASE_URL / REDIS_URL / JWT_SECRET_KEY

# 3. Apply migrations
alembic upgrade head

# 4. Run
uvicorn app.main:app --reload
```

- API docs: `http://localhost:8000/docs` (Swagger) and `/redoc`.
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`.
- Health: `GET /api/v1/health` (liveness), `GET /api/v1/ready` (readiness —
  checks DB + Redis, returns 503 if degraded).

## Database migrations

Migrations are Alembic, generated against a live database and reviewed by hand.
The initial migration also creates the required `citext` and `pgcrypto`
extensions and drops the PostgreSQL ENUM types on downgrade (SQLAlchemy creates
enum types implicitly but does not drop them).

```bash
alembic revision --autogenerate -m "describe change"   # generate
alembic upgrade head                                    # apply
alembic downgrade -1                                    # roll back one
```

## Quality gates

```bash
ruff check app tests     # lint (import order, style, bugbear, async)
mypy app                 # strict static typing
pytest -q                # tests
```

All three are green as of Phase 6. See `../../docs/phase-6-backend-initialization.md`.
