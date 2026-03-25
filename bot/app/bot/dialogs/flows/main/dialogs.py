from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row, WebApp
from aiogram_dialog.widgets.text import Const, Format

from app.bot.dialogs.flows.main.getters import get_main
from app.bot.dialogs.flows.main.handlers import on_cart, on_catalog
from app.bot.dialogs.flows.main.states import MainSG

main_dialog = Dialog(
    Window(
        Format(
            "👋 Привет, <b>{name}</b>!\n\n"
            "Добро пожаловать в наш магазин.\n"
            "Выбери, что тебя интересует:"
        ),
        WebApp(
            Const("🛍 Открыть Магазин"),
            url=Format("{webapp_url}"),
            id="webapp",
        ),
        Row(
            Button(Const("📦 Каталог"), id="catalog", on_click=on_catalog),
            Button(Const("🛒 Корзина"), id="cart", on_click=on_cart),
        ),
        Const(
            "\n<i>Также можешь написать <code>@botusername вопрос</code> "
            "для поиска в FAQ</i>",
            when="show_hint",
        ),
        state=MainSG.main,
        getter=get_main,
    )
)
