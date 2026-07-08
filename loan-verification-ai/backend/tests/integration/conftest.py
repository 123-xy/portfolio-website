from __future__ import annotations

import subprocess
import sys
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.domain.value_objects.enums import ApplicationStatus, UserRole
from app.infrastructure.auth.password_hasher import Argon2PasswordHasher
from app.infrastructure.db.models.officer import Officer
from app.infrastructure.db.models.user import User

BACKEND_ROOT = Path(__file__).resolve().parents[2]

# Every application table that integration tests might write to, in an order
# that satisfies FK constraints when truncated with CASCADE (CASCADE makes
# the order mostly irrelevant, but listing them explicitly documents what a
# test run touches).
_APP_TABLES = [
    "audit_logs",
    "reports",
    "officer_decisions",
    "verification_results",
    "risk_scores",
    "artifacts",
    "co_applicants",
    "applications",
    "notifications",
    "refresh_tokens",
    "officers",
    "users",
]


@pytest.fixture(scope="session", autouse=True)
def _migrate_test_database() -> None:
    """Apply every migration to the dedicated integration test database once
    per test session. Runs as a subprocess (real `alembic upgrade head`,
    exactly as ops would run it) against the DATABASE_URL the root conftest
    already pointed at `verify_test` before any `app.*` import happened."""
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_ROOT,
        check=True,
        capture_output=True,
    )


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """A direct database session for test setup/assertions that go around the
    API — e.g. seeding a staff user (self-registration can't grant elevated
    roles) or inserting a risk score without running the real AI pipeline."""
    settings = get_settings()
    engine = create_async_engine(str(settings.database_url))
    sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
        await session.commit()
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _truncate_after_test(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    yield
    tables = ", ".join(_APP_TABLES)
    await db_session.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    await db_session.commit()


class FakePipelineDispatcher:
    """Test double for the Celery dispatch port. Integration tests exercise
    the API/DB/storage wiring, not the AI pipeline itself (that's covered by
    the pipeline's own unit tests and by manual live verification) — so
    `submit` only needs to be recorded, not actually enqueued to a worker."""

    def __init__(self) -> None:
        self.dispatched: list[uuid.UUID] = []

    def dispatch(self, application_id: uuid.UUID) -> None:
        self.dispatched.append(application_id)


@pytest.fixture
def fake_dispatcher() -> FakePipelineDispatcher:
    return FakePipelineDispatcher()


@pytest_asyncio.fixture
async def client(
    fake_dispatcher: FakePipelineDispatcher,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    from app.interfaces.api.v1.deps.applications import get_pipeline_dispatcher
    from app.main import create_app, lifespan

    app = create_app()
    app.dependency_overrides[get_pipeline_dispatcher] = lambda: fake_dispatcher

    async with lifespan(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


async def register_applicant(
    client: httpx.AsyncClient,
    *,
    email: str,
    password: str = "Str0ngPass!234",
    full_name: str = "Test Applicant",
) -> dict[str, str]:
    """Self-registers via the real API (role is always forced to applicant
    server-side, by design — see Phase 7)."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name, "role": "applicant"},
    )
    assert response.status_code == 201, response.text
    return dict(response.json())


async def seed_staff_user(
    db_session: AsyncSession,
    *,
    email: str,
    password: str,
    full_name: str,
    role: UserRole,
    employee_code: str,
) -> uuid.UUID:
    """Officers/auditors/admins are provisioned out-of-band, not
    self-registered — this mirrors Phase 11's seed migration but as a
    per-test fixture so each test gets an isolated staff account."""
    user = User(
        email=email,
        password_hash=Argon2PasswordHasher().hash(password),
        full_name=full_name,
        role=role,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    if role in (UserRole.OFFICER, UserRole.AUDITOR):
        db_session.add(Officer(user_id=user.id, employee_code=employee_code, branch_code="HQ"))

    await db_session.commit()
    return user.id


async def login(client: httpx.AsyncClient, *, email: str, password: str) -> dict[str, str]:
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return dict(response.json())


def auth_headers(tokens: dict[str, str]) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


async def mark_pending_review(db_session: AsyncSession, application_id: str) -> None:
    """These integration tests never run the real AI pipeline (the dispatch
    port is faked — see `FakePipelineDispatcher`), so a `submitted`
    application never naturally reaches `pending_review` on its own. Officer
    decisions require that status, so tests exercising the decision flow move
    it there directly, standing in for "the pipeline finished scoring it"."""
    await db_session.execute(
        text("UPDATE applications SET status = :status WHERE id = :id"),
        {"status": ApplicationStatus.PENDING_REVIEW.value, "id": uuid.UUID(application_id)},
    )
    await db_session.commit()
