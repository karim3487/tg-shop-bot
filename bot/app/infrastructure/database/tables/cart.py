from app.infrastructure.database.connection.base import BaseConnection
from app.infrastructure.database.models.cart import CartItemModel
from app.infrastructure.database.tables.base import BaseTable

_ITEM_COLS = """
    ci.id, ci.client_id, ci.product_id, ci.quantity,
    p.name AS product_name, p.price AS product_price,
    (SELECT pi.image FROM catalog_productimage pi
     WHERE pi.product_id = p.id ORDER BY pi."order" LIMIT 1) AS product_image
"""


class CartTable(BaseTable):
    __tablename__ = "cart_cartitem"

    def __init__(self, connection: BaseConnection):
        self.connection = connection

    async def get_items(self, *, client_id: int) -> list[CartItemModel]:
        data = await self.connection.fetchmany(
            sql=f"""
                SELECT {_ITEM_COLS}
                FROM cart_cartitem ci
                JOIN catalog_product p ON p.id = ci.product_id
                WHERE ci.client_id = %s
                ORDER BY ci.id
            """,
            params=(client_id,),
        )
        return data.to_models(CartItemModel) or []

    async def get_item(self, *, item_id: int, client_id: int) -> CartItemModel | None:
        data = await self.connection.fetchone(
            sql=f"""
                SELECT {_ITEM_COLS}
                FROM cart_cartitem ci
                JOIN catalog_product p ON p.id = ci.product_id
                WHERE ci.id = %s AND ci.client_id = %s
            """,
            params=(item_id, client_id),
        )
        return data.to_model(CartItemModel)

    async def add_or_increment(self, *, client_id: int, product_id: int) -> None:
        await self.connection.execute(
            sql="""
                INSERT INTO cart_cartitem (client_id, product_id, quantity)
                VALUES (%s, %s, 1)
                ON CONFLICT (client_id, product_id)
                DO UPDATE SET quantity = cart_cartitem.quantity + 1
            """,
            params=(client_id, product_id),
        )

    async def update_quantity(self, *, item_id: int, client_id: int, delta: int) -> int | None:
        data = await self.connection.fetchone(
            sql="""
                UPDATE cart_cartitem 
                SET quantity = quantity + %s 
                WHERE id = %s AND client_id = %s 
                RETURNING quantity
            """,
            params=(delta, item_id, client_id),
        )
        if not data:
            return None
        return int(data.data.get("quantity", 0))

    async def remove(self, *, item_id: int, client_id: int) -> None:
        await self.connection.execute(
            sql="DELETE FROM cart_cartitem WHERE id = %s AND client_id = %s",
            params=(item_id, client_id),
        )

    async def clear(self, *, client_id: int) -> None:
        await self.connection.execute(
            sql="DELETE FROM cart_cartitem WHERE client_id = %s",
            params=(client_id,),
        )
