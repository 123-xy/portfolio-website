"""seed demo officer account

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-11 00:00:00.000000
"""
from collections.abc import Sequence

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# ---------------------------------------------------------------------------
# DEV/DEMO SEED — NOT FOR PRODUCTION.
#
# Officers are provisioned out-of-band (no self-registration; see Phase 7),
# and there is no admin user-management UI yet. This migration seeds exactly
# one officer account, with fixed IDs, so the officer dashboard is reachable
# without a manual DB insert. The Argon2id hash below is for the password
# "OfficerDemo123!" — it is intentionally checked in as a known dev/staging
# credential.
#
# Production deployments MUST remove this migration (or rotate the password
# and disable/delete the account) before go-live — a hardcoded credential in
# version control is never acceptable in production. See docs/phase-11-*.md.
# ---------------------------------------------------------------------------

_OFFICER_USER_ID = "00000000-0000-0000-0000-000000000101"
_OFFICER_PROFILE_ID = "00000000-0000-0000-0000-000000000102"
_OFFICER_EMAIL = "officer@verifyco.bank"
_OFFICER_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$KIUQIkSolZKydq41ZmyNUQ$"
    "B0w9V7m0GbnL8uSH9R39t+cOdbg6/L/U/GMMS1zBtxw"
)

_UPGRADE_SQL = f"""
    INSERT INTO users (id, email, password_hash, full_name, role, is_active, created_at, updated_at)
    VALUES (
        '{_OFFICER_USER_ID}',
        '{_OFFICER_EMAIL}',
        '{_OFFICER_PASSWORD_HASH}',
        'Priya Officer',
        'officer',
        true,
        now(),
        now()
    )
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO officers (id, user_id, employee_code, branch_code, department, created_at, updated_at)
    VALUES (
        '{_OFFICER_PROFILE_ID}',
        '{_OFFICER_USER_ID}',
        'EMP-0001',
        'HQ',
        'Retail Lending',
        now(),
        now()
    )
    ON CONFLICT (id) DO NOTHING;
"""

_DOWNGRADE_SQL = f"""
    DELETE FROM officers WHERE id = '{_OFFICER_PROFILE_ID}';
    DELETE FROM users WHERE id = '{_OFFICER_USER_ID}';
"""


def upgrade() -> None:
    op.execute(_UPGRADE_SQL)


def downgrade() -> None:
    op.execute(_DOWNGRADE_SQL)
