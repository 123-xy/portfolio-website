# backend/ — FastAPI service (Clean Architecture)

REST API, authentication, orchestration of the AI pipeline, and all
database access. The dependency rule is strict: **arrows point inward**;
inner layers never import outer layers, and `domain/` has zero third-party
imports.

```
app/
  domain/            # innermost, pure Python — entities, value objects, domain services, exceptions
  application/       # use cases + ports (interfaces the domain needs from the outside world)
    ports/           #   repositories/ and services/ — abstract interfaces (Protocols/ABCs)
    use_cases/       #   one class per business operation (SubmitApplication, RecordOfficerDecision, ...)
    dto/             #   framework-independent request/response data objects
  infrastructure/    # implements application/ports — the ONLY layer allowed 3rd-party imports
    db/              #   SQLAlchemy models, repositories, Alembic migrations
    storage/         #   S3-compatible object storage adapter (boto3)
    ai/              #   adapters onto the ai-services package (face/speech/intent/fraud/risk)
    tasks/           #   Celery task definitions — thin adapters that call use_cases
    auth/            #   JWT provider, password hasher
    notifications/   #   email / in-app notifiers
  interfaces/        # outermost — HTTP presentation
    api/v1/          #   routers/, schemas/ (Pydantic), deps/ (FastAPI Depends providers)
    middleware/      #   request-id, error handling, logging, auth
  core/              # config (pydantic-settings), DI container (composition root), logging

tests/
  unit/              # domain + use-case tests with mocked ports
  integration/       # repository/adapter tests against real Postgres/Redis/MinIO
  api/               # endpoint tests through the ASGI app
```

Why this shape: the AI implementations (InsightFace, Whisper, Gemini) are
expected to change over the platform's life. Because `application/` depends
only on port *interfaces*, swapping any `infrastructure/ai/*` adapter never
touches a use case, a router, or a test. `core/container.py` is the single
composition root that binds each port to its concrete implementation.

See `../../docs/phase-2-architecture-design.md` §2.
