from aiogram_dialog import DialogManager

from app.infrastructure.database.db import DB
from app.infrastructure.database.models.client import ClientModel


async def get_confirm(dialog_manager: DialogManager, db: DB, client: ClientModel | None, **kwargs) -> dict:
    data = dialog_manager.dialog_data
    if client is None:
        return {"full_name": "", "phone": "", "address": "", "items_text": "", "total": "0"}

    items = await db.cart.get_items(client_id=client.id)
    total = sum(i.subtotal for i in items)
    lines = "\n".join(f"  • {i.product_name} × {i.quantity} = {i.subtotal} ₽" for i in items)

    return {
        "full_name": data.get("full_name", ""),
        "phone": client.phone or "—",
        "address": data.get("address", ""),
        "items_text": lines,
        "total": str(total),
    }


async def get_payment(dialog_manager: DialogManager, **kwargs) -> dict:
    data = dialog_manager.dialog_data
    return {
        "order_id": data.get("order_id", ""),
        "order_total": data.get("order_total", "0"),
        "order_items_text": data.get("order_items_text", ""),
    }
