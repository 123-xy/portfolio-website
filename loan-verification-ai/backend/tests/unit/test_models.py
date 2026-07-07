from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

import app.infrastructure.db.models  # noqa: F401  (registers all tables)
from app.infrastructure.db.base import Base

EXPECTED_TABLES = {
    "users",
    "refresh_tokens",
    "officers",
    "applications",
    "co_applicants",
    "artifacts",
    "verification_results",
    "risk_scores",
    "officer_decisions",
    "reports",
    "audit_logs",
    "notifications",
    "risk_engine_config",
}


def test_all_domain_tables_registered() -> None:
    assert EXPECTED_TABLES.issubset(set(Base.metadata.tables.keys()))


def test_every_table_compiles_for_postgres() -> None:
    dialect = postgresql.dialect()
    for table in Base.metadata.tables.values():
        # Raises if a column/constraint type cannot be rendered for Postgres.
        assert str(CreateTable(table).compile(dialect=dialect))
