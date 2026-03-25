from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from app.infrastructure.database.models.client import ClientModel


class IsAdmin(BaseFilter):
    """Passes only if the current user has role 'admin' or 'owner'."""

    async def __call__(self, event: Message | CallbackQuery, client: ClientModel | None = None) -> bool:
        return client is not None and client.is_admin
