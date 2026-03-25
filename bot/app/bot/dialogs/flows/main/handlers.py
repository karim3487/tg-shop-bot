from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from app.bot.dialogs.flows.cart.states import CartSG
from app.bot.dialogs.flows.catalog.states import CatalogSG


async def on_catalog(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    await manager.start(CatalogSG.categories, mode=StartMode.RESET_STACK)


async def on_cart(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    await manager.start(CartSG.cart, mode=StartMode.RESET_STACK)
