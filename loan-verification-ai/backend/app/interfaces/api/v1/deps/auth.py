from __future__ import annotations

from collections.abc import Callable, Coroutine
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.auth import AuthenticatedUser
from app.application.ports.repositories.refresh_token_repository import RefreshTokenRepository
from app.application.ports.repositories.user_repository import UserRepository
from app.application.ports.services.password_hasher import PasswordHasher
from app.application.ports.services.token_service import TokenService
from app.application.use_cases.auth.authenticate_user import AuthenticateUser
from app.application.use_cases.auth.logout_user import LogoutUser
from app.application.use_cases.auth.refresh_tokens import RefreshAccessToken
from app.application.use_cases.auth.register_user import RegisterUser
from app.application.use_cases.auth.token_issuer import TokenIssuer
from app.core.config import Settings, get_settings
from app.domain.exceptions import AuthenticationError, AuthorizationError
from app.domain.value_objects.enums import UserRole
from app.infrastructure.auth.password_hasher import Argon2PasswordHasher
from app.infrastructure.auth.token_service import JwtTokenService
from app.infrastructure.db.repositories.refresh_token_repository import (
    SqlAlchemyRefreshTokenRepository,
)
from app.infrastructure.db.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.db.session import get_db_session

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

# HTTPBearer with auto_error off so a missing token yields our own domain error
# (consistent envelope) rather than FastAPI's default 403.
_bearer = HTTPBearer(auto_error=False)


# --- Singletons (construction is non-trivial; build once per process) ---
@lru_cache
def _password_hasher() -> PasswordHasher:
    # Building the Argon2 CryptContext is non-trivial; cache one per process.
    return Argon2PasswordHasher()


def get_password_hasher() -> PasswordHasher:
    return _password_hasher()


def get_token_service(settings: SettingsDep) -> TokenService:
    # Construction is trivial (stores a few config values), so build per request.
    return JwtTokenService(settings)


# --- Request-scoped repositories ---
def get_user_repository(session: SessionDep) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_refresh_token_repository(session: SessionDep) -> RefreshTokenRepository:
    return SqlAlchemyRefreshTokenRepository(session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]
RefreshRepoDep = Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)]
HasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


def get_token_issuer(tokens: TokenServiceDep, refresh_repo: RefreshRepoDep) -> TokenIssuer:
    return TokenIssuer(tokens, refresh_repo)


TokenIssuerDep = Annotated[TokenIssuer, Depends(get_token_issuer)]


# --- Use case providers ---
def get_register_user(
    users: UserRepoDep, hasher: HasherDep, issuer: TokenIssuerDep
) -> RegisterUser:
    return RegisterUser(users, hasher, issuer)


def get_authenticate_user(
    users: UserRepoDep, hasher: HasherDep, issuer: TokenIssuerDep, settings: SettingsDep
) -> AuthenticateUser:
    return AuthenticateUser(
        users,
        hasher,
        issuer,
        max_attempts=settings.max_failed_login_attempts,
        lockout_minutes=settings.account_lockout_minutes,
    )


def get_refresh_access_token(
    users: UserRepoDep,
    refresh_repo: RefreshRepoDep,
    tokens: TokenServiceDep,
    issuer: TokenIssuerDep,
) -> RefreshAccessToken:
    return RefreshAccessToken(users, refresh_repo, tokens, issuer)


def get_logout_user(refresh_repo: RefreshRepoDep, tokens: TokenServiceDep) -> LogoutUser:
    return LogoutUser(refresh_repo, tokens)


# --- Authentication / RBAC ---
async def get_current_user(
    users: UserRepoDep,
    tokens: TokenServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> AuthenticatedUser:
    """Resolve and validate the bearer access token into the current user.
    Raises AuthenticationError (401) if the token is missing/invalid or the
    user no longer exists or is inactive."""
    if credentials is None:
        raise AuthenticationError("Missing bearer token.")

    claims = tokens.decode_access_token(credentials.credentials)
    user = await users.get_by_id(claims.user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("User not found or inactive.")

    return AuthenticatedUser(
        id=user.id, email=user.email, full_name=user.full_name, role=user.role
    )


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


def require_role(
    *allowed: UserRole,
) -> Callable[[AuthenticatedUser], Coroutine[Any, Any, AuthenticatedUser]]:
    """Dependency factory enforcing that the current user holds one of the
    allowed roles. RBAC is enforced server-side on the endpoint, not merely in
    the UI."""

    async def _dependency(user: CurrentUser) -> AuthenticatedUser:
        if user.role not in allowed:
            raise AuthorizationError("You do not have access to this resource.")
        return user

    return _dependency


def client_context(request: Request) -> tuple[str | None, str | None]:
    """Best-effort (user_agent, ip) for audit/session metadata."""
    ip = request.client.host if request.client else None
    return request.headers.get("user-agent"), ip
