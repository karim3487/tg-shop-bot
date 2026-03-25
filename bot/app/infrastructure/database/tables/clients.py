from app.infrastructure.database.connection.base import BaseConnection
from app.infrastructure.database.models.client import ClientModel
from app.infrastructure.database.tables.base import BaseTable

_COLS = "id, telegram_id, username, first_name, last_name, phone, role, is_active, created_at"


class ClientsTable(BaseTable):
    __tablename__ = "clients_client"

    def __init__(self, connection: BaseConnection):
        self.connection = connection

    async def get_all_active_telegram_ids(self) -> list[int]:
        data = await self.connection.fetchmany(
            sql="SELECT telegram_id FROM clients_client WHERE is_active = TRUE",
        )
        return [row["telegram_id"] for row in data]

    async def get_by_id(self, *, client_id: int) -> ClientModel | None:
        data = await self.connection.fetchone(
            sql=f"SELECT {_COLS} FROM clients_client WHERE id = %s",
            params=(client_id,),
        )
        return data.to_model(ClientModel)

    async def get_by_telegram_id(self, *, telegram_id: int) -> ClientModel | None:
        data = await self.connection.fetchone(
            sql=f"SELECT {_COLS} FROM clients_client WHERE telegram_id = %s",
            params=(telegram_id,),
        )
        return data.to_model(ClientModel)

    async def update_phone(self, *, telegram_id: int, phone: str) -> None:
        await self.connection.execute(
            sql="UPDATE clients_client SET phone = %s WHERE telegram_id = %s",
            params=(phone, telegram_id),
        )

    async def upsert(
        self,
        *,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> ClientModel:
        data = await self.connection.update_and_fetchone(
            sql=f"""
                INSERT INTO clients_client
                    (telegram_id, username, first_name, last_name, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, 'user', TRUE, NOW())
                ON CONFLICT (telegram_id) DO UPDATE
                    SET username   = EXCLUDED.username,
                        first_name = EXCLUDED.first_name,
                        last_name  = EXCLUDED.last_name
                RETURNING {_COLS}
            """,
            params=(telegram_id, username, first_name, last_name),
        )
        return data.to_model(ClientModel, raise_if_empty=True)
