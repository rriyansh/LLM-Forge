"""Async SQLAlchemy session factory."""
from __future__ import annotations

import os
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.models import Base
from src.utils.config_parser import get_env_int
from src.utils.logger import get_logger

log = get_logger(__name__)

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine():
    global _engine, _session_factory
    if _engine is None:
        url = os.getenv("DATABASE_URL")
        if not url:
            return None
        _engine = create_async_engine(
            url,
            pool_size=get_env_int("DB_POOL_SIZE", 10),
            max_overflow=get_env_int("DB_MAX_OVERFLOW", 20),
            pool_pre_ping=True,
            pool_recycle=1800,
            echo=False,
        )
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


async def init_db() -> None:
    eng = get_engine()
    if eng is None:
        log.warning("db_not_configured")
        return
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("db_initialized")


async def get_session() -> AsyncIterator[AsyncSession]:
    eng = get_engine()
    if eng is None or _session_factory is None:
        raise RuntimeError("Database not configured")
    async with _session_factory() as session:
        yield session
