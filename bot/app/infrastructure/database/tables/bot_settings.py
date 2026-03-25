from app.infrastructure.database.connection.base import BaseConnection
from app.infrastructure.database.tables.base import BaseTable


class BotSettingsTable(BaseTable):
    __tablename__ = "bot_settings"

    def __init__(self, connection: BaseConnection):
        self.connection = connection

    async def get_active_channels(self) -> list[dict]:
        data = await self.connection.fetchmany(
            sql="SELECT channel_id, title, invite_link FROM bot_settings_requiredchannel WHERE is_active = TRUE",
        )
        return data.as_dicts()

    async def get_admin_chat_id(self) -> str | None:
        data = await self.connection.fetchone(
            sql="SELECT admin_chat_id FROM bot_settings_botconfig LIMIT 1",
        )
        if data.is_empty():
            return None
        return data.data.get("admin_chat_id") or None
