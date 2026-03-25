import operator

from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Back, Button, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from app.bot.dialogs.flows.catalog.getters import (
    get_categories,
    get_product,
    get_products,
    get_subcategories,
)
from app.bot.dialogs.flows.catalog.handlers import (
    on_add_to_cart,
    on_back_from_product,
    on_back_to_main,
    on_catalog_start,
    on_category_click,
    on_go_to_cart,
    on_product_click,
    on_share_product,
    on_subcategory_click,
)
from app.bot.dialogs.flows.catalog.states import CatalogSG

catalog_dialog = Dialog(
    # ── Root categories ───────────────────────────────────────
    Window(
        Const("🛍 <b>Каталог</b>\n\nВыбери категорию:"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="s_cats",
                item_id_getter=operator.itemgetter(1),
                items="categories",
                on_click=on_category_click,
            ),
            id="sg_cats",
            width=2,
            height=6,
        ),
        Button(Const("🔙 Назад"), id="back_main", on_click=on_back_to_main),
        state=CatalogSG.categories,
        getter=get_categories,
    ),

    # ── Subcategories ─────────────────────────────────────────
    Window(
        Format("📂 <b>{title}</b>\n\nВыбери подкатегорию:"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="s_subcats",
                item_id_getter=operator.itemgetter(1),
                items="subcategories",
                on_click=on_subcategory_click,
            ),
            id="sg_subcats",
            width=2,
            height=6,
        ),
        Back(Const("🔙 Назад")),
        state=CatalogSG.subcategories,
        getter=get_subcategories,
    ),

    # ── Products list ─────────────────────────────────────────
    Window(
        Format("📦 <b>{title}</b>\n\nВыбери товар:"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="s_prods",
                item_id_getter=operator.itemgetter(1),
                items="products",
                on_click=on_product_click,
            ),
            id="sg_prods",
            width=1,
            height=6,
        ),
        Back(Const("🔙 Назад")),
        state=CatalogSG.products,
        getter=get_products,
    ),

    # ── Product detail ────────────────────────────────────────
    Window(
        StaticMedia(
            path=Format("{image_path}"),
            type=ContentType.PHOTO,
            when="image_path",
        ),
        Format(
            "<b>{name}</b>\n\n"
            "{description}\n\n"
            "💰 <b>Цена: {price} ₽</b>"
        ),
        Row(
            Button(Const("🛒 В корзину"), id="add_cart", on_click=on_add_to_cart),
            Button(Const("🛒 Перейти в корзину"), id="go_cart", on_click=on_go_to_cart),
        ),
        Row(
            Button(Const("🔙 Назад"), id="back_product", on_click=on_back_from_product),
            Button(Const("🔗 Поделиться"), id="share_product", on_click=on_share_product),
        ),
        state=CatalogSG.product,
        getter=get_product,
    ),
    on_start=on_catalog_start,
)
