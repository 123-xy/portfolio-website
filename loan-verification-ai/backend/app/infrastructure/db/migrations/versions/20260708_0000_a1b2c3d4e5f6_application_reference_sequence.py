"""application reference number sequence

Revision ID: a1b2c3d4e5f6
Revises: b601e4eacebc
Create Date: 2026-07-08 00:00:00.000000
"""
from collections.abc import Sequence

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "b601e4eacebc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # A dedicated sequence produces human-facing reference numbers
    # (APP-<year>-<zero-padded seq>). Using a sequence — rather than counting
    # rows — is concurrency-safe and gap-tolerant, which is what matters for a
    # display reference (uniqueness, not contiguity).
    op.execute("CREATE SEQUENCE IF NOT EXISTS application_reference_seq START WITH 1")


def downgrade() -> None:
    op.execute("DROP SEQUENCE IF EXISTS application_reference_seq")
