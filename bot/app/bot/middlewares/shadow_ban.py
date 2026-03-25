import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from app.infrastructure.database.models.client import ClientModel

logger = logging.getLogger(__name__)


class ShadowBanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        client: ClientModel | None = data.get("client")

        if client is None:
            return await handler(event, data)

        if not client.is_active:
            logger.warning("Inactive user tried to interact: %d", client.telegram_id)
            if event.callback_query:
                await event.callback_query.answer()
            return

        return await handler(event, data)
