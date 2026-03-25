import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update
from psycopg_pool import AsyncConnectionPool

from app.infrastructure.database.connection.psycopg_connection import PsycopgConnection
from app.infrastructure.database.db import DB

logger = logging.getLogger(__name__)


class DataBaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        db_pool: AsyncConnectionPool = data.get("db_pool")

        if db_pool is None:
            logger.error("Database pool is not provided in middleware data.")
            raise RuntimeError("Missing db_pool in middleware context.")

        async with db_pool.connection() as raw_connection:
            await raw_connection.set_autocommit(True)
            connection = PsycopgConnection(raw_connection)
            data["db"] = DB(connection)
            return await handler(event, data)
