import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update, User
from redis.asyncio import Redis

from app.infrastructure.database.db import DB
from app.infrastructure.database.models.client import ClientModel

logger = logging.getLogger(__name__)


class GetUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")

        if user is None:
            return await handler(event, data)

        db: DB = data.get("db")
        redis: Redis = data.get("redis")
        if db is None or redis is None:
            logger.error("Missing `db` or `redis` in middleware context.")
            raise RuntimeError("Missing dependencies in middleware context.")

        cache_key = f"user:{user.id}"
        cached_user = await redis.get(cache_key)

        if cached_user:
            try:
                client = ClientModel.model_validate_json(cached_user)
                data["client"] = client
                return await handler(event, data)
            except Exception as e:
                logger.error("Failed to deserialize cached user for %d: %s", user.id, e)

        client: ClientModel | None = await db.clients.get_by_telegram_id(telegram_id=user.id)
        data["client"] = client

        if client:
            try:
                await redis.setex(
                    name=cache_key,
                    time=300,
                    value=client.model_dump_json()
                )
            except Exception as e:
                logger.error("Failed to cache user for %d: %s", user.id, e)

        return await handler(event, data)
