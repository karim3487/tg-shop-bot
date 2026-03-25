import operator

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Back, Button, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Case, Const, Format

from app.bot.dialogs.flows.cart.getters import get_cart, get_item_manage
from app.bot.dialogs.flows.cart.handlers import (
    on_back_to_main,
    on_checkout,
    on_clear,
    on_decrease,
    on_increase,
    on_item_select,
    on_remove,
)
from app.bot.dialogs.flows.cart.states import CartSG

cart_dialog = Dialog(
    # ── Cart overview ─────────────────────────────────────────
    Window(
        Case(
            {
                True: Const("🛒 Ваша корзина пуста."),
                False: Format("🛒 <b>Ваша корзина:</b>\n\n{items_text}\n\n<b>Итого: {total} ₽</b>"),
            },
            selector="is_empty",
        ),
        ScrollingGroup(
            Select(
                Format("✏️ {item[0]}"),
                id="s_cart",
                item_id_getter=operator.itemgetter(1),
                items="items",
                on_click=on_item_select,
            ),
            id="sg_cart",
            width=1,
            height=5,
            when=lambda data, widget, manager: not data.get("is_empty"),
        ),
        Row(
            Button(Const("🗑 Очистить"), id="clear", on_click=on_clear,
                   when=lambda data, widget, manager: not data.get("is_empty")),
            Button(Const("✅ Оформить"), id="checkout", on_click=on_checkout,
                   when=lambda data, widget, manager: not data.get("is_empty")),
        ),
        Button(Const("🔙 Назад"), id="back_main", on_click=on_back_to_main),
        state=CartSG.cart,
        getter=get_cart,
    ),

    # ── Manage specific item ──────────────────────────────────
    Window(
        Format(
            "✏️ <b>{item_name}</b>\n\n"
            "Цена: {price} ₽\n"
            "Количество: <b>{quantity}</b>\n"
            "Сумма: {subtotal} ₽"
        ),
        Row(
            Button(Const("➖"), id="decrease", on_click=on_decrease),
            Button(Const("➕"), id="increase", on_click=on_increase),
        ),
        Button(Const("❌ Убрать из корзины"), id="remove", on_click=on_remove),
        Back(Const("🔙 К корзине")),
        state=CartSG.item_manage,
        getter=get_item_manage,
    ),
)
