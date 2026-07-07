from enum import Enum
from typing import TypeVar

from sqlalchemy import Enum as SAEnum

E = TypeVar("E", bound=Enum)


def pg_enum(enum_cls: type[E], name: str) -> SAEnum:
    """Build a PostgreSQL ENUM column type that persists the enum *value*
    (e.g. 'explicit_yes') rather than the member name ('EXPLICIT_YES'), under a
    stable type name shared across the schema."""
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=True,
        values_callable=lambda cls: [member.value for member in cls],
        validate_strings=True,
    )
