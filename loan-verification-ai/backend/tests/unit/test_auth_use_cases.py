from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.application.dto.auth import LoginCommand, RefreshCommand, RegisterCommand
from app.application.ports.repositories.refresh_token_repository import RefreshTokenRepository
from app.application.ports.repositories.user_repository import UserRepository
from app.application.ports.services.password_hasher import PasswordHasher
from app.application.use_cases.auth.authenticate_user import AuthenticateUser
from app.application.use_cases.auth.refresh_tokens import RefreshAccessToken
from app.application.use_cases.auth.register_user import RegisterUser
from app.application.use_cases.auth.token_issuer import TokenIssuer
from app.core.config import Settings
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.user import User
from app.domain.exceptions import AuthenticationError, ConflictError
from app.domain.value_objects.enums import UserRole
from app.infrastructure.auth.token_service import JwtTokenService


class FakePasswordHasher(PasswordHasher):
    """Deterministic, fast stand-in — verifies a fixed reversible transform."""

    def hash(self, password: str) -> str:
        return f"hashed::{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed::{password}"


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._by_id: dict[uuid.UUID, User] = {}

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._by_id.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._by_id.values() if u.email == email), None)

    async def email_exists(self, email: str) -> bool:
        return any(u.email == email for u in self._by_id.values())

    async def create(
        self, *, email: str, full_name: str, password_hash: str, role: UserRole
    ) -> User:
        user = User(
            id=uuid.uuid4(),
            email=email,
            full_name=full_name,
            role=role,
            password_hash=password_hash,
        )
        self._by_id[user.id] = user
        return user

    async def update(self, user: User) -> None:
        self._by_id[user.id] = user


class FakeRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self) -> None:
        self._by_id: dict[uuid.UUID, RefreshToken] = {}

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
        user_agent: str | None,
        ip_address: str | None,
    ) -> RefreshToken:
        token = RefreshToken(
            id=uuid.uuid4(), user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        self._by_id[token.id] = token
        return token

    async def get_active_by_hash(self, token_hash: str) -> RefreshToken | None:
        return next(
            (
                t
                for t in self._by_id.values()
                if t.token_hash == token_hash and t.revoked_at is None
            ),
            None,
        )

    async def revoke(self, token_id: uuid.UUID, *, replaced_by: uuid.UUID | None = None) -> None:
        token = self._by_id.get(token_id)
        if token:
            token.revoked_at = datetime.now(UTC)

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        for token in self._by_id.values():
            if token.user_id == user_id:
                token.revoked_at = datetime.now(UTC)


def _token_service() -> JwtTokenService:
    return JwtTokenService(Settings(jwt_secret_key="auth-usecase-test-secret-abcdefghij"))


def _build() -> tuple[FakeUserRepository, FakeRefreshTokenRepository, TokenIssuer]:
    users = FakeUserRepository()
    refresh = FakeRefreshTokenRepository()
    issuer = TokenIssuer(_token_service(), refresh)
    return users, refresh, issuer


async def test_register_creates_user_and_issues_tokens() -> None:
    users, _, issuer = _build()
    use_case = RegisterUser(users, FakePasswordHasher(), issuer)

    pair = await use_case.execute(
        RegisterCommand(email="A@Bank.com", full_name="A B", password="pw")
    )

    assert pair.access_token and pair.refresh_token
    # Email is normalized to lowercase on storage.
    assert await users.get_by_email("a@bank.com") is not None


async def test_register_duplicate_email_conflicts() -> None:
    users, _, issuer = _build()
    use_case = RegisterUser(users, FakePasswordHasher(), issuer)
    await use_case.execute(RegisterCommand(email="dup@bank.com", full_name="A B", password="pw"))

    with pytest.raises(ConflictError):
        await use_case.execute(
            RegisterCommand(email="dup@bank.com", full_name="A B", password="pw")
        )


async def test_login_locks_account_after_max_attempts() -> None:
    users, refresh, issuer = _build()
    hasher = FakePasswordHasher()
    await RegisterUser(users, hasher, issuer).execute(
        RegisterCommand(email="lock@bank.com", full_name="A B", password="correct")
    )
    login = AuthenticateUser(users, hasher, issuer, max_attempts=3, lockout_minutes=15)

    for _ in range(3):
        with pytest.raises(AuthenticationError):
            await login.execute(LoginCommand(email="lock@bank.com", password="wrong"))

    # Even the correct password is refused while locked.
    with pytest.raises(AuthenticationError):
        await login.execute(LoginCommand(email="lock@bank.com", password="correct"))
    user = await users.get_by_email("lock@bank.com")
    assert user is not None and user.is_locked(datetime.now(UTC))


async def test_login_generic_error_does_not_reveal_missing_user() -> None:
    users, _, issuer = _build()
    login = AuthenticateUser(users, FakePasswordHasher(), issuer)
    with pytest.raises(AuthenticationError) as exc:
        await login.execute(LoginCommand(email="ghost@bank.com", password="x"))
    assert "Invalid email or password" in str(exc.value)


async def test_refresh_rotation_revokes_old_token() -> None:
    users, refresh, issuer = _build()
    hasher = FakePasswordHasher()
    tokens = _token_service()
    pair = await RegisterUser(users, hasher, issuer).execute(
        RegisterCommand(email="rot@bank.com", full_name="A B", password="pw")
    )

    rotate = RefreshAccessToken(users, refresh, tokens, issuer)
    new_pair = await rotate.execute(RefreshCommand(refresh_token=pair.refresh_token))
    assert new_pair.refresh_token != pair.refresh_token

    # The original refresh token is now revoked and cannot be reused.
    with pytest.raises(AuthenticationError):
        await rotate.execute(RefreshCommand(refresh_token=pair.refresh_token))


async def test_expired_refresh_token_is_rejected() -> None:
    users, refresh, issuer = _build()
    tokens = _token_service()
    # Build a user + a manually-expired token row.
    real_user = await users.create(
        email="exp@bank.com", full_name="A B", password_hash="x", role=UserRole.APPLICANT
    )
    material = tokens.create_refresh_token()
    stored = await refresh.create(
        user_id=real_user.id,
        token_hash=material.token_hash,
        expires_at=datetime.now(UTC) - timedelta(seconds=1),
        user_agent=None,
        ip_address=None,
    )
    assert stored.is_active(datetime.now(UTC)) is False

    rotate = RefreshAccessToken(users, refresh, tokens, issuer)
    with pytest.raises(AuthenticationError):
        await rotate.execute(RefreshCommand(refresh_token=material.raw))
