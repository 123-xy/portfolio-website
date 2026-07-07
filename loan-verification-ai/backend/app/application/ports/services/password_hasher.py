from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Port for password hashing/verification. Implemented in infrastructure so
    the algorithm (Argon2) can be swapped without touching use cases."""

    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, password: str, password_hash: str) -> bool: ...
