"""Composition root.

The single place that binds application-layer *ports* (interfaces) to their
concrete `infrastructure` implementations. Routers depend on use cases; use
cases depend on ports; only this module knows the concrete wiring — so swapping
an implementation (e.g. a different face-match provider or storage backend)
touches nothing but the binding here.

Feature wiring is added as those features land in later phases; for Phase 6 the
container exposes the database session factory that the API depends on.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_db_session


async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session
