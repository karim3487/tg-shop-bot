import logging

import redis.asyncio as aioredis
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from psycopg_pool import AsyncConnectionPool

from app.bot.callbacks import OrderActionCallback
from app.config.models import AppConfig
from app.infrastructure.database.connection.psycopg_connection import PsycopgConnection
from app.infrastructure.database.db import DB

logger = logging.getLogger(__name__)

CHANNEL = "new_order"


class AdminNotifierService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def notify_new_order(self, db: DB, order_id: int) -> None:
        admin_chat_id = await db.settings.get_admin_chat_id()
        if not admin_chat_id:
            logger.warning(
                "admin_chat_id not configured — skipping notification for order #%s",
                order_id
            )
            return

        order = await db.orders.get_by_id(order_id=order_id)
        if not order:
            logger.warning("Order #%s not found — skipping notification", order_id)
            return

        items = await db.orders.get_items(order_id=order_id)
        items_lines = "\n".join(f"  • {i.product_name} × {i.quantity}" for i in items)

        text = (
            f"🛒 <b>Новый заказ #{order.id}</b>  [⏳ Ожидает]\n\n"
            f"👤 {order.full_name}\n"
            f"📱 {order.phone or '—'}\n"
            f"📍 {order.address}\n\n"
            f"<b>Товары:</b>\n{items_lines}\n\n"
            f"<b>Сумма: {order.total_price} ₽</b>"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚙️ В обработке",
                    callback_data=OrderActionCallback(
                        order_id=order.id, action="processing"
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data=OrderActionCallback(
                        order_id=order.id, action="cancelled"
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Завершить",
                    callback_data=OrderActionCallback(
                        order_id=order.id, action="delivered"
                    ).pack(),
                ),
            ]
        ])

        try:
            await self.bot.send_message(
                chat_id=admin_chat_id,
                text=text,
                reply_markup=kb,
            )
            logger.info(
                "New order #%s notification sent to admin chat %s",
                order_id,
                admin_chat_id
            )
        except Exception:
            logger.exception("Failed to send admin notification for order #%s", order_id)


async def order_notifier_worker(bot: Bot, db_pool: AsyncConnectionPool, config: AppConfig) -> None:
    """Subscribes to the Redis 'new_order' channel and sends a simple admin notification."""
    redis_url = (
        f"redis://:{config.redis.password}@"
        f"{config.redis.host}:{config.redis.port}/{config.redis.database}"
    )
    # pub/sub requires its own dedicated connection
    redis_client = aioredis.from_url(redis_url, decode_responses=True)
    notifier = AdminNotifierService(bot)

    try:
        async with redis_client.pubsub() as pubsub:
            await pubsub.subscribe(CHANNEL)
            logger.info("Order notifier subscribed to Redis channel '%s'", CHANNEL)

            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue

                try:
                    order_id = int(message["data"])
                except (ValueError, TypeError):
                    logger.warning("Invalid message on '%s': %r", CHANNEL, message["data"])
                    continue

                try:
                    async with db_pool.connection() as conn:
                        db = DB(PsycopgConnection(conn))
                        await notifier.notify_new_order(db, order_id)
                except Exception:
                    logger.exception("Failed to send admin notification for order #%s", order_id)
    finally:
        await redis_client.aclose()
