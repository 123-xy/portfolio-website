from __future__ import annotations

from app.application.dto.auth import RegisterCommand, TokenPair
from app.application.ports.repositories.user_repository import UserRepository
from app.application.ports.services.password_hasher import PasswordHasher
from app.application.use_cases.auth.token_issuer import TokenIssuer
from app.domain.exceptions import ConflictError


class RegisterUser:
    """Create an account and immediately issue a token pair.

    Email is normalized to a canonical form and uniqueness is enforced before
    hashing, so a duplicate registration fails fast without doing crypto work.
    """

    def __init__(
        self,
        users: UserRepository,
        password_hasher: PasswordHasher,
        token_issuer: TokenIssuer,
    ) -> None:
        self._users = users
        self._hasher = password_hasher
        self._token_issuer = token_issuer

    async def execute(
        self,
        command: RegisterCommand,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenPair:
        email = command.email.strip().lower()
        if await self._users.email_exists(email):
            raise ConflictError("An account with this email already exists.")

        user = await self._users.create(
            email=email,
            full_name=command.full_name.strip(),
            password_hash=self._hasher.hash(command.password),
            role=command.role,
        )
        return await self._token_issuer.issue(user, user_agent=user_agent, ip_address=ip_address)
