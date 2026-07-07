from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.application.dto.auth import LoginCommand, TokenPair
from app.application.ports.repositories.user_repository import UserRepository
from app.application.ports.services.password_hasher import PasswordHasher
from app.application.use_cases.auth.token_issuer import TokenIssuer
from app.domain.exceptions import AuthenticationError

# A single generic message for every failure mode so the API never reveals
# whether an email exists (defeats user enumeration).
_INVALID_CREDENTIALS = "Invalid email or password."


class AuthenticateUser:
    """Verify credentials and issue tokens, with brute-force lockout.

    After `max_attempts` consecutive failures the account is locked for
    `lockout_minutes`; a successful login resets the counter.
    """

    def __init__(
        self,
        users: UserRepository,
        password_hasher: PasswordHasher,
        token_issuer: TokenIssuer,
        *,
        max_attempts: int = 5,
        lockout_minutes: int = 15,
    ) -> None:
        self._users = users
        self._hasher = password_hasher
        self._token_issuer = token_issuer
        self._max_attempts = max_attempts
        self._lockout_minutes = lockout_minutes

    async def execute(self, command: LoginCommand) -> TokenPair:
        now = datetime.now(UTC)
        email = command.email.strip().lower()
        user = await self._users.get_by_email(email)

        if user is None:
            raise AuthenticationError(_INVALID_CREDENTIALS)
        if user.is_locked(now):
            raise AuthenticationError("Account is temporarily locked. Try again later.")
        if not user.is_active:
            raise AuthenticationError("Account is disabled.")

        if not self._hasher.verify(command.password, user.password_hash):
            user.failed_login_count += 1
            if user.failed_login_count >= self._max_attempts:
                user.locked_until = now + timedelta(minutes=self._lockout_minutes)
                user.failed_login_count = 0
            await self._users.update(user)
            raise AuthenticationError(_INVALID_CREDENTIALS)

        # Success — clear any accumulated failures and record the login.
        user.failed_login_count = 0
        user.locked_until = None
        user.last_login_at = now
        await self._users.update(user)

        return await self._token_issuer.issue(
            user, user_agent=command.user_agent, ip_address=command.ip_address
        )
