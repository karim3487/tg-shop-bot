from app.infrastructure.database.connection.base import BaseConnection
from app.infrastructure.database.models.faq import FAQItemModel
from app.infrastructure.database.tables.base import BaseTable

_COLS = "id, question, answer, is_active"


class FAQTable(BaseTable):
    __tablename__ = "faq_faqitem"

    def __init__(self, connection: BaseConnection):
        self.connection = connection

    async def get_all(self) -> list[FAQItemModel]:
        data = await self.connection.fetchmany(
            sql=f"SELECT {_COLS} FROM faq_faqitem WHERE is_active = TRUE ORDER BY id",
        )
        return data.to_models(FAQItemModel) or []

    async def search(self, *, query: str, limit: int = 8) -> list[FAQItemModel]:
        data = await self.connection.fetchmany(
            sql=f"""
                SELECT {_COLS} FROM faq_faqitem
                WHERE is_active = TRUE
                  AND (question ILIKE %s OR answer ILIKE %s)
                ORDER BY id LIMIT %s
            """,
            params=(f"%{query}%", f"%{query}%", limit),
        )
        return data.to_models(FAQItemModel) or []
