from dataclasses import dataclass

from app.infrastructure.database.connection.base import BaseConnection
from app.infrastructure.database.tables.base import BaseTable


@dataclass
class BroadcastRow:
    id: int
    text: str
    image: str | None  # relative path, e.g. "broadcasts/photo.jpg"


class BroadcastsTable(BaseTable):
    __tablename__ = "broadcasts_broadcast"

    def __init__(self, connection: BaseConnection):
        self.connection = connection

    async def get_pending(self) -> list[BroadcastRow]:
        data = await self.connection.fetchmany(
            sql="SELECT id, text, image FROM broadcasts_broadcast WHERE status = 'ready' ORDER BY created_at",
        )
        return [BroadcastRow(id=r["id"], text=r["text"], image=r["image"] or None) for r in data]

    async def set_sending(self, *, broadcast_id: int) -> None:
        await self.connection.execute(
            sql="UPDATE broadcasts_broadcast SET status = 'sending' WHERE id = %s",
            params=(broadcast_id,),
        )

    async def finish(self, *, broadcast_id: int, sent_count: int, error_count: int) -> None:
        await self.connection.execute(
            sql="""
                UPDATE broadcasts_broadcast
                SET status = 'sent', sent_count = %s, error_count = %s, sent_at = NOW()
                WHERE id = %s
            """,
            params=(sent_count, error_count, broadcast_id),
        )
