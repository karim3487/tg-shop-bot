import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Update, User

from app.bot.callbacks import CheckSubscriptionCallback
from app.infrastructure.database.db import DB

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    """Checks that the user is subscribed to all required channels."""

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        db: DB | None = data.get("db")
        bot: Bot = data["bot"]
        if db is None:
            return await handler(event, data)

        channels = await db.settings.get_active_channels()

        if not channels:
            return await handler(event, data)

        not_subscribed = []
        for ch in channels:
            try:
                member = await bot.get_chat_member(chat_id=ch["channel_id"], user_id=user.id)
                if member.status in ("left", "kicked"):
                    not_subscribed.append(ch)
            except Exception:
                logger.warning("Could not check subscription for channel %s", ch["channel_id"])

        if not not_subscribed:
            return await handler(event, data)

        # Build subscribe buttons
        buttons = [
            [InlineKeyboardButton(text=f"📢 {ch['title']}", url=ch["invite_link"])]
            for ch in not_subscribed
        ]
        buttons.append(
            [InlineKeyboardButton(text="✅ Я подписался", callback_data=CheckSubscriptionCallback().pack())]
        )
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        message = event.message or (event.callback_query.message if event.callback_query else None)
        if message:
            await message.answer(
                "👋 Для использования бота необходимо подписаться на наши каналы:",
                reply_markup=kb,
            )
        elif event.callback_query:
            await event.callback_query.answer("Сначала подпишитесь на каналы!", show_alert=True)
