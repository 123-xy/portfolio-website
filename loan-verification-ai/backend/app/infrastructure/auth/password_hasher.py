from passlib.context import CryptContext

from app.application.ports.services.password_hasher import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    """Argon2id password hashing via passlib. Argon2id is the current OWASP
    recommendation for password storage (memory-hard, resistant to GPU/ASIC
    cracking)."""

    def __init__(self) -> None:
        self._context = CryptContext(schemes=["argon2"], deprecated="auto")

    def hash(self, password: str) -> str:
        return str(self._context.hash(password))

    def verify(self, password: str, password_hash: str) -> bool:
        return bool(self._context.verify(password, password_hash))
