"""seed default active risk engine config

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-07-08 01:00:00.000000
"""
from collections.abc import Sequence

from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The Phase 1/2 default weights (Face Match 40% / Speech 20% / Intent 20% /
# Fraud 20%) and the Phase 3 example thresholds, seeded as the initial active
# configuration so the risk engine always has a config to read.
_UPGRADE_SQL = """
    INSERT INTO risk_engine_config (id, version, weights, thresholds, is_active, created_at)
    VALUES (
        gen_random_uuid(),
        1,
        '{"face_match": 0.40, "speech": 0.20, "intent": 0.20, "fraud": 0.20}'::jsonb,
        '{"low_max": 0.33, "medium_max": 0.66}'::jsonb,
        true,
        now()
    )
    ON CONFLICT (version) DO NOTHING
"""


def upgrade() -> None:
    op.execute(_UPGRADE_SQL)


def downgrade() -> None:
    op.execute("DELETE FROM risk_engine_config WHERE version = 1")
