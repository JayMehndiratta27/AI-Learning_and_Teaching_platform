"""Database access: MongoDB (Motor) or automatic SQLite fallback."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional, Union

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import get_settings

if TYPE_CHECKING:
    from sqlite_backend import SqliteDatabase

logger = logging.getLogger(__name__)

_backend: Optional[str] = None
_mongo_client: Optional[AsyncIOMotorClient] = None
_sqlite_db: Optional[Any] = None


async def init_database() -> None:
    """Call once at app startup. Picks Mongo or SQLite (auto if Mongo unreachable)."""
    global _backend, _mongo_client, _sqlite_db
    settings = get_settings()
    mode = (settings.database_mode or "auto").lower()

    if mode == "sqlite":
        from sqlite_backend import SqliteDatabase

        _backend = "sqlite"
        _sqlite_db = await SqliteDatabase.create(settings.sqlite_path)
        logger.info("LearnFlow storage: SQLite (%s)", settings.sqlite_path)
        return

    if mode == "mongo":
        _backend = "mongo"
        _mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
        logger.info("LearnFlow storage: MongoDB (%s)", settings.mongodb_db_name)
        return

    # auto — prefer Mongo, fall back to SQLite for zero-setup local runs
    try:
        client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=2500)
        await client.admin.command("ping")
        _mongo_client = client
        _backend = "mongo"
        logger.info("LearnFlow storage: MongoDB (%s)", settings.mongodb_db_name)
    except Exception as exc:
        from sqlite_backend import SqliteDatabase

        logger.warning("MongoDB not available (%s) — using SQLite fallback", exc)
        _backend = "sqlite"
        _sqlite_db = await SqliteDatabase.create(settings.sqlite_path)
        logger.info("LearnFlow storage: SQLite (%s)", settings.sqlite_path)


def get_database() -> Union[AsyncIOMotorDatabase, Any]:
    if _backend == "sqlite":
        if _sqlite_db is None:
            raise RuntimeError("Database not initialized — await init_database() in app lifespan")
        return _sqlite_db
    if _mongo_client is None:
        raise RuntimeError("Database not initialized — await init_database() in app lifespan")
    return _mongo_client[get_settings().mongodb_db_name]


async def close_db() -> None:
    global _mongo_client, _sqlite_db
    if _backend == "sqlite" and _sqlite_db is not None:
        await _sqlite_db.close()
        _sqlite_db = None
    elif _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None


def storage_label() -> str:
    return _backend or "unknown"
