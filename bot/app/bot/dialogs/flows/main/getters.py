from aiogram_dialog import DialogManager

from app.infrastructure.database.models.client import ClientModel


async def get_main(dialog_manager: DialogManager, client: ClientModel | None, **kwargs) -> dict:
    name = client.display_name if client else "гость"
    webapp_url = dialog_manager.middleware_data.get("webapp_url", "")
    return {"name": name, "show_hint": True, "webapp_url": webapp_url}
