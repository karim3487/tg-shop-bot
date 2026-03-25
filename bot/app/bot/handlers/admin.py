import logging
import re

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.callbacks import OrderActionCallback
from app.bot.filters import IsAdmin
from app.infrastructure.database.db import DB

logger = logging.getLogger(__name__)

admin_router = Router()
admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())

STATUS_LABELS = {
    "pending":    "⏳ Ожидает оплаты",
    "paid":       "💳 Оплачен",
    "processing": "⚙️ В обработке",
    "shipped":    "🚚 Отправлен",
    "delivered":  "✅ Доставлен",
    "cancelled":  "❌ Отменён",
}

# Human-readable short labels for buttons
_BTN_LABELS = {
    "pending":    "⏳ Ожидает",
    "paid":       "💳 Оплачен",
    "processing": "⚙️ В обработке",
    "shipped":    "🚚 Отправлен",
    "delivered":  "✅ Доставлен",
    "cancelled":  "❌ Отменить",
}

# Allowed next statuses per current status
_TRANSITIONS: dict[str, list[str]] = {
    "pending":    ["paid", "processing", "cancelled"],
    "paid":       ["processing", "shipped", "cancelled"],
    "processing": ["shipped", "delivered", "cancelled"],
    "shipped":    ["delivered", "cancelled"],
    "delivered":  [],
    "cancelled":  [],
}


def _order_kb(order_id: int, current_status: str) -> InlineKeyboardMarkup | None:
    next_statuses = _TRANSITIONS.get(current_status, [])
    if not next_statuses:
        return None
    buttons = [
        InlineKeyboardButton(
            text=_BTN_LABELS[s],
            callback_data=OrderActionCallback(order_id=order_id, action=s).pack(),
        )
        for s in next_statuses
    ]
    # Two buttons per row
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _order_text(order_id: int, full_name: str, phone: str, address: str,
                items_line: str, total: str, status: str) -> str:
    label = STATUS_LABELS.get(status, status)
    return (
        f"🛒 <b>Заказ #{order_id}</b>  [{label}]\n\n"
        f"👤 {full_name}\n"
        f"📱 {phone}\n"
        f"📍 {address}\n\n"
        f"<b>Товары:</b>\n{items_line}\n\n"
        f"<b>Сумма: {total} ₽</b>"
    )


async def _notify_user(bot: Bot, telegram_id: int, order_id: int, status: str) -> None:
    label = STATUS_LABELS.get(status, status)
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=f"📦 <b>Заказ #{order_id}</b>\nСтатус изменён: <b>{label}</b>",
        )
    except Exception as e:
        logger.warning("Failed to notify user %s about order #%s: %s", telegram_id, order_id, e)


@admin_router.callback_query(OrderActionCallback.filter())
async def cb_order_action(
    callback: CallbackQuery,
    callback_data: OrderActionCallback,
    db: DB,
    bot: Bot,
) -> None:
    order_id = callback_data.order_id
    new_status = callback_data.action

    order = await db.orders.get_by_id(order_id=order_id)
    if not order:
        await callback.answer("Заказ не найден.", show_alert=True)
        return

    if order.status == new_status:
        await callback.answer("Статус уже установлен.", show_alert=True)
        return

    allowed = _TRANSITIONS.get(order.status, [])
    if new_status not in allowed:
        await callback.answer("Переход недоступен.", show_alert=True)
        return

    from app.infrastructure.database.exceptions import StateConflictError

    try:
        await db.orders.update_status(
            order_id=order_id,
            status=new_status,
            expected_old_status=order.status,
        )
    except StateConflictError:
        await callback.answer(
            "⚠️ This order's status was already changed by another admin.",
            show_alert=True,
        )
        # Remove buttons since the state is no longer valid
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    # Update message text and keyboard
    label = STATUS_LABELS[new_status]
    try:
        original = callback.message.text or ""
        new_text = re.sub(r"\[.*?\]", f"[{label}]", original, count=1)
        new_kb = _order_kb(order_id, new_status)
        await callback.message.edit_text(new_text, parse_mode="HTML", reply_markup=new_kb)
    except Exception as e:
        logger.warning("Failed to edit admin message: %s", e)

    await callback.answer(f"Статус → {label}")

    # Notify the user
    client = await db.clients.get_by_id(client_id=order.client_id)
    if client:
        await _notify_user(bot, client.telegram_id, order_id, new_status)


@admin_router.message(Command("orders"))
async def cmd_orders(message: Message, db: DB) -> None:
    admin_chat_id = await db.settings.get_admin_chat_id()

    if not admin_chat_id or str(message.chat.id) != str(admin_chat_id):
        return

    orders = await db.orders.get_active()
    if not orders:
        await message.answer("Нет активных заказов.")
        return

    for order in orders:
        await message.answer(
            _order_text(
                order_id=order.id,
                full_name=order.full_name,
                phone=order.phone,
                address=order.address,
                items_line="—",
                total=str(order.total_price),
                status=order.status,
            ),
            reply_markup=_order_kb(order.id, order.status),
        )
