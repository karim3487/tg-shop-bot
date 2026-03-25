from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Row
from aiogram_dialog.widgets.text import Const, Format

from app.bot.dialogs.flows.order.getters import get_confirm, get_payment
from app.bot.dialogs.flows.order.handlers import (
    on_address,
    on_cancel,
    on_cancel_order,
    on_confirm,
    on_full_name,
    on_paid,
)
from app.bot.dialogs.flows.order.states import OrderSG

order_dialog = Dialog(
    # ── Full name ─────────────────────────────────────────────
    Window(
        Const(
            "📝 <b>Оформление заказа</b>\n\n"
            "Шаг 1/2 — Введите ваше <b>ФИО</b>:"
        ),
        TextInput(id="full_name", type_factory=str, on_success=on_full_name),
        Back(Const("❌ Отмена")),
        state=OrderSG.full_name,
    ),

    # ── Address ───────────────────────────────────────────────
    Window(
        Const("📍 Шаг 2/2 — Введите <b>адрес доставки</b>:"),
        TextInput(id="address", type_factory=str, on_success=on_address),
        Back(Const("🔙 Назад")),
        state=OrderSG.address,
    ),

    # ── Confirmation ──────────────────────────────────────────
    Window(
        Format(
            "📋 <b>Проверьте заказ:</b>\n\n"
            "<b>ФИО:</b> {full_name}\n"
            "<b>Телефон:</b> {phone}\n"
            "<b>Адрес:</b> {address}\n\n"
            "<b>Товары:</b>\n{items_text}\n\n"
            "<b>Итого: {total} ₽</b>"
        ),
        Row(
            Button(Const("✅ Подтвердить"), id="confirm", on_click=on_confirm),
            Button(Const("❌ Отмена"), id="cancel", on_click=on_cancel),
        ),
        state=OrderSG.confirm,
        getter=get_confirm,
    ),

    # ── Payment ───────────────────────────────────────────────
    Window(
        Format(
            "💳 <b>Оплата заказа #{order_id}</b>\n\n"
            "<b>Товары:</b>\n{order_items_text}\n\n"
            "<b>Итого: {order_total} ₽</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Переведите сумму на карту:\n"
            "<code>1234 5678 9012 3456</code>\n"
            "Получатель: <b>Иван И.</b>\n\n"
            "После оплаты нажмите кнопку ниже."
        ),
        Row(
            Button(Const("✅ Я оплатил(а)"), id="paid", on_click=on_paid),
            Button(Const("❌ Отменить заказ"), id="cancel_order", on_click=on_cancel_order),
        ),
        state=OrderSG.payment,
        getter=get_payment,
    ),
)
