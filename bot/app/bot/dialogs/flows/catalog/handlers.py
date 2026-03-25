import asyncio
import logging
import os

import aiohttp
from aiogram import Bot
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select

from app.bot.dialogs.flows.cart.states import CartSG
from app.bot.dialogs.flows.catalog.states import CatalogSG
from app.bot.dialogs.flows.main.states import MainSG
from app.infrastructure.database.db import DB
from app.infrastructure.database.models.client import ClientModel

logger = logging.getLogger(__name__)

_IMG_CACHE_DIR = "/tmp/tg_shop_images"


async def _fetch_bytes(url: str) -> bytes | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.read()
    except Exception as e:
        logger.warning("Failed to fetch image %s: %s", url, e)
    return None


async def cache_product_image(product_id: int, index: int, url: str) -> str | None:
    """Download image to disk cache. Returns local path or None."""
    os.makedirs(_IMG_CACHE_DIR, exist_ok=True)
    path = os.path.join(_IMG_CACHE_DIR, f"product_{product_id}_{index}.jpg")
    if os.path.exists(path):
        return path
    data = await _fetch_bytes(url)
    if data:

        def _save():
            with open(path, "wb") as f:
                f.write(data)

        await asyncio.to_thread(_save)
        return path
    return None


async def on_catalog_start(start_data: dict, manager: DialogManager) -> None:
    """Copy start_data into dialog_data (used when starting from deep link)."""
    if isinstance(start_data, dict):
        manager.dialog_data.update(start_data)


async def on_back_to_main(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    await manager.start(MainSG.main, mode=StartMode.RESET_STACK)


async def on_category_click(
    callback: CallbackQuery,
    widget: Select,
    manager: DialogManager,
    item_id: str,
) -> None:
    category_id = int(item_id)
    db: DB = manager.middleware_data["db"]

    subcats = await db.catalog.get_subcategories(parent_id=category_id)
    # parent_category_id — для окна подкатегорий (не перезаписывается при выборе подкатегории)
    # category_id — для окна товаров (меняется при выборе подкатегории)
    manager.dialog_data["parent_category_id"] = category_id
    manager.dialog_data["category_id"] = category_id

    if subcats:
        await manager.switch_to(CatalogSG.subcategories)
    else:
        await manager.switch_to(CatalogSG.products)


async def on_subcategory_click(
    callback: CallbackQuery,
    widget: Select,
    manager: DialogManager,
    item_id: str,
) -> None:
    # Обновляем только category_id для товаров; parent_category_id остаётся неизменным
    manager.dialog_data["category_id"] = int(item_id)
    await manager.switch_to(CatalogSG.products)


async def on_product_click(
    callback: CallbackQuery,
    widget: Select,
    manager: DialogManager,
    item_id: str,
) -> None:
    product_id = int(item_id)
    db: DB = manager.middleware_data["db"]
    media_base_url: str = manager.middleware_data.get("media_base_url", "")

    bot: Bot = manager.middleware_data["bot"]

    # Clean up MediaGroup from a previously viewed product
    await _delete_media_group(bot, callback.message.chat.id, manager)

    image_path: str | None = None
    photo_count: int = 0

    if media_base_url:
        images = await db.catalog.get_product_images(product_id=product_id)
        photo_count = len(images)

        if len(images) == 1:
            # Single photo — embed directly in the dialog window (one clean message)
            url = f"{media_base_url.rstrip('/')}/{images[0].image}"
            image_path = await cache_product_image(product_id, 0, url)

        elif len(images) > 1:
            # Multiple photos — send as album, then force dialog to send new message below
            media_group: list[InputMediaPhoto] = []
            for i, img in enumerate(images[:10]):
                url = f"{media_base_url.rstrip('/')}/{img.image}"
                path = await cache_product_image(product_id, i, url)
                if path:
                    media_group.append(InputMediaPhoto(media=FSInputFile(path)))

            if media_group:
                sent = await callback.message.answer_media_group(media=media_group)
                manager.dialog_data["media_group_msg_ids"] = [m.message_id for m in sent]
                # Delete the current dialog message so aiogram-dialog sends a new one
                # BELOW the album (instead of editing the old message above it)
                try:
                    await callback.message.delete()
                except Exception:
                    pass

    manager.dialog_data["product_id"] = product_id
    manager.dialog_data["image_path"] = image_path
    manager.dialog_data["photo_count"] = photo_count
    await manager.switch_to(CatalogSG.product)


async def _delete_media_group(bot: Bot, chat_id: int, manager: DialogManager) -> None:
    """Delete MediaGroup messages from a previously viewed product."""
    msg_ids: list[int] = manager.dialog_data.pop("media_group_msg_ids", [])
    for msg_id in msg_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass


async def on_back_from_product(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    """Custom Back handler that cleans up the MediaGroup album before navigating back."""
    bot: Bot = manager.middleware_data["bot"]
    await _delete_media_group(bot, callback.message.chat.id, manager)
    await manager.back()


async def on_add_to_cart(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    product_id = int(manager.dialog_data["product_id"])
    db: DB = manager.middleware_data["db"]
    client: ClientModel | None = manager.middleware_data.get("client")

    if client is None:
        await callback.answer("Сначала нажми /start", show_alert=True)
        return

    await db.cart.add_or_increment(client_id=client.id, product_id=product_id)
    await callback.answer("✅ Добавлено в корзину!")


async def on_go_to_cart(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    await manager.start(CartSG.cart, mode=StartMode.RESET_STACK)


async def on_share_product(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    bot: Bot = manager.middleware_data["bot"]
    product_id = int(manager.dialog_data["product_id"])
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=product_{product_id}"
    await callback.message.answer(
        f"🔗 Ссылка на товар:\n{link}",
        disable_web_page_preview=True,
    )
    await callback.answer()
