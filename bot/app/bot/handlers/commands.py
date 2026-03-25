import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InputMediaPhoto,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram_dialog import DialogManager, StartMode

from app.bot.callbacks import CheckSubscriptionCallback
from app.bot.dialogs.flows.cart.states import CartSG
from app.bot.dialogs.flows.catalog.states import CatalogSG
from app.bot.dialogs.flows.catalog.handlers import cache_product_image
from app.bot.dialogs.flows.main.states import MainSG
from app.infrastructure.database.db import DB

logger = logging.getLogger(__name__)

commands_router = Router()

_CONTACT_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


@commands_router.message(CommandStart())
async def cmd_start(
    message: Message,
    command: CommandObject,
    dialog_manager: DialogManager,
    db: DB,
) -> None:
    client = await db.clients.upsert(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    if not client.phone:
        await message.answer(
            "👋 Добро пожаловать!\n\n"
            "Для продолжения поделитесь номером телефона:",
            reply_markup=_CONTACT_KB,
        )
        return

    # Deep link: /start product_<id>
    if command.args and command.args.startswith("product_"):
        await _open_product_from_deep_link(command.args, message, dialog_manager, db)
        return

    await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)


async def _open_product_from_deep_link(
    args: str,
    message: Message,
    dialog_manager: DialogManager,
    db: DB,
) -> None:
    try:
        product_id = int(args.split("_", 1)[1])
    except (ValueError, IndexError):
        await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)
        return

    product = await db.catalog.get_product(product_id=product_id)
    if not product:
        await message.answer("❌ Товар не найден.")
        await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)
        return

    images = await db.catalog.get_product_images(product_id=product_id)
    photo_count = len(images)
    image_path: str | None = None
    media_group_msg_ids: list[int] = []
    media_base_url: str = dialog_manager.middleware_data.get("media_base_url", "")

    if media_base_url and images:
        if len(images) == 1:
            url = f"{media_base_url.rstrip('/')}/{images[0].image}"
            image_path = await cache_product_image(product_id, 0, url)
        else:
            media_group = []
            for i, img in enumerate(images[:10]):
                url = f"{media_base_url.rstrip('/')}/{img.image}"
                path = await cache_product_image(product_id, i, url)
                if path:
                    media_group.append(InputMediaPhoto(media=FSInputFile(path)))
            if media_group:
                sent = await message.answer_media_group(media=media_group)
                media_group_msg_ids = [m.message_id for m in sent]

    await dialog_manager.start(
        CatalogSG.product,
        mode=StartMode.RESET_STACK,
        data={
            "product_id": product_id,
            "image_path": image_path,
            "photo_count": photo_count,
            "media_group_msg_ids": media_group_msg_ids,
            "parent_category_id": product.category_id,
            "category_id": product.category_id,
        },
    )


@commands_router.message(F.contact)
async def handle_contact(
    message: Message,
    dialog_manager: DialogManager,
    db: DB,
) -> None:
    # Accept only the user's own contact, not forwarded ones
    if message.contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, поделитесь своим собственным контактом.")
        return

    await db.clients.update_phone(
        telegram_id=message.from_user.id,
        phone=message.contact.phone_number,
    )

    await message.answer("✅ Контакт сохранён!", reply_markup=ReplyKeyboardRemove())
    await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)


@commands_router.message(Command("catalog"))
async def cmd_catalog(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(CatalogSG.categories, mode=StartMode.RESET_STACK)


@commands_router.message(Command("cart"))
async def cmd_cart(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(CartSG.cart, mode=StartMode.RESET_STACK)


@commands_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "ℹ️ <b>Как пользоваться ботом:</b>\n\n"
        "🛍 /catalog — каталог товаров\n"
        "🛒 /cart — корзина\n\n"
        "Напиши <code>@botusername вопрос</code> для поиска в FAQ.\n\n"
        "/start — главное меню"
    )


@commands_router.callback_query(CheckSubscriptionCallback.filter())
async def cb_check_subscription(callback: CallbackQuery, dialog_manager: DialogManager) -> None:
    await callback.answer("Проверяем подписку...")
    await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)
