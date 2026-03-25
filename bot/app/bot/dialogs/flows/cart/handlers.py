from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Select

from app.bot.dialogs.flows.cart.states import CartSG
from app.bot.dialogs.flows.main.states import MainSG
from app.bot.dialogs.flows.order.states import OrderSG
from app.infrastructure.database.db import DB
from app.infrastructure.database.models.client import ClientModel


async def on_item_select(
    callback: CallbackQuery,
    widget: Select,
    manager: DialogManager,
    item_id: str,
) -> None:
    manager.dialog_data["selected_item_id"] = int(item_id)
    await manager.switch_to(CartSG.item_manage)


async def on_increase(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    db: DB = manager.middleware_data["db"]
    client: ClientModel | None = manager.middleware_data.get("client")
    if not client:
        return

    item_id = int(manager.dialog_data["selected_item_id"])
    await db.cart.update_quantity(item_id=item_id, client_id=client.id, delta=1)


async def on_decrease(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    db: DB = manager.middleware_data["db"]
    client: ClientModel | None = manager.middleware_data.get("client")
    if not client:
        return

    item_id = int(manager.dialog_data["selected_item_id"])
    new_qty = await db.cart.update_quantity(item_id=item_id, client_id=client.id, delta=-1)
    if new_qty is not None and new_qty <= 0:
        await db.cart.remove(item_id=item_id, client_id=client.id)
        await manager.switch_to(CartSG.cart)


async def on_remove(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    db: DB = manager.middleware_data["db"]
    client: ClientModel | None = manager.middleware_data.get("client")
    if not client:
        return

    item_id = int(manager.dialog_data["selected_item_id"])
    await db.cart.remove(item_id=item_id, client_id=client.id)
    await manager.switch_to(CartSG.cart)


async def on_clear(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    db: DB = manager.middleware_data["db"]
    client: ClientModel | None = manager.middleware_data.get("client")
    if not client:
        return
    await db.cart.clear(client_id=client.id)
    await callback.answer("🗑 Корзина очищена")


async def on_back_to_main(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    await manager.start(MainSG.main, mode=StartMode.RESET_STACK)


async def on_checkout(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    client: ClientModel | None = manager.middleware_data.get("client")
    if not client:
        await callback.answer("Сначала нажми /start", show_alert=True)
        return

    db: DB = manager.middleware_data["db"]
    items = await db.cart.get_items(client_id=client.id)
    if not items:
        await callback.answer("Корзина пуста!", show_alert=True)
        return

    await manager.start(OrderSG.full_name, mode=StartMode.RESET_STACK)
