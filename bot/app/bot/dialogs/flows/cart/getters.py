from aiogram_dialog import DialogManager

from app.infrastructure.database.db import DB
from app.infrastructure.database.models.client import ClientModel


async def get_cart(
    dialog_manager: DialogManager, db: DB, client: ClientModel | None, **kwargs
) -> dict:
    if client is None:
        return {"items": [], "items_text": "Нет данных", "total": "0", "is_empty": True}

    items = await db.cart.get_items(client_id=client.id)
    if not items:
        return {"items": [], "items_text": "", "total": "0", "is_empty": True}

    lines = "\n".join(
        f"🔸 {i.product_name} × {i.quantity} = {i.subtotal} ₽" for i in items
    )
    total = sum(i.subtotal for i in items)
    return {
        "items": [(f"{i.product_name} × {i.quantity} = {i.subtotal} ₽", str(i.id)) for i in items],
        "items_text": lines,
        "total": str(total),
        "is_empty": False,
    }


async def get_item_manage(
    dialog_manager: DialogManager, db: DB, client: ClientModel | None, **kwargs
) -> dict:
    if client is None:
        return {"item_name": "", "quantity": 0, "price": "0", "subtotal": "0"}

    item_id = int(dialog_manager.dialog_data.get("selected_item_id", 0))
    item = await db.cart.get_item(item_id=item_id, client_id=client.id)

    if not item:
        return {"item_name": "Товар не найден", "quantity": 0, "price": "0", "subtotal": "0"}

    return {
        "item_name": item.product_name,
        "quantity": item.quantity,
        "price": str(item.product_price),
        "subtotal": str(item.subtotal),
    }
