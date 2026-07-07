import logging

from redis.asyncio import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.infrastructure.db.session import get_engine

logger = logging.getLogger("app.health")


async def check_database() -> bool:
    """True if a trivial query succeeds against the database."""
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.warning("database_health_check_failed", exc_info=True)
        return False


async def check_redis() -> bool:
    """True if Redis responds to PING."""
    settings = get_settings()
    client: Redis = Redis.from_url(str(settings.redis_url))
    try:
        return bool(await client.ping())
    except Exception:
        logger.warning("redis_health_check_failed", exc_info=True)
        return False
    finally:
        await client.aclose()
