import logging
import os

import httpx
from django_rq import job

logger = logging.getLogger(__name__)

STATUS_LABELS = {
    "pending": "⏳ Ожидает оплаты",
    "paid": "💳 Оплачен",
    "processing": "⚙️ В обработке",
    "shipped": "🚚 Отправлен",
    "delivered": "✅ Доставлен",
    "cancelled": "❌ Отменён",
}


@job
def notify_order_status(telegram_id: int, order_id: int, status: str) -> None:
    """Отправляет уведомление пользователю об изменении статуса заказа."""
    token = os.environ.get("BOT_TOKEN")
    if not token:
        logger.warning("BOT_TOKEN не задан — уведомление не отправлено")
        return

    label = STATUS_LABELS.get(status, status)
    text = (
        f"📦 <b>Заказ #{order_id}</b>\n"
        f"Статус изменён: <b>{label}</b>"
    )

    try:
        response = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": telegram_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        response.raise_for_status()
        logger.info("Уведомление отправлено пользователю %s (заказ #%s)", telegram_id, order_id)
    except Exception as e:
        logger.error("Ошибка отправки уведомления: %s", e)


# Redis connection pool for performance
_redis_pool = None


def _get_redis_client():
    from django.conf import settings
    import redis

    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            username=settings.REDIS_USERNAME or None,
            password=settings.REDIS_PASSWORD or None,
            db=settings.REDIS_DB,
        )
    return redis.Redis(connection_pool=_redis_pool)


@job
def publish_new_order(order_id: int) -> None:
    """Публикует событие о новом заказе в Redis-канал — бот подхватит и отправит уведомление."""
    try:
        client = _get_redis_client()
        client.publish("new_order", order_id)
        logger.info("Событие new_order #%s опубликовано в Redis", order_id)
    except Exception as e:
        logger.error("Ошибка публикации события new_order #%s: %s", order_id, e)
