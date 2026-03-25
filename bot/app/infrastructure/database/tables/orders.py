from decimal import Decimal

from app.infrastructure.database.connection.base import BaseConnection
from app.infrastructure.database.models.order import OrderItemModel, OrderModel
from app.infrastructure.database.tables.base import BaseTable

_ORDER_COLS = "id, client_id, full_name, phone, address, status, total_price, created_at"


class OrdersTable(BaseTable):
    __tablename__ = "orders_order"

    def __init__(self, connection: BaseConnection):
        self.connection = connection

    async def create(
        self,
        *,
        client_id: int,
        full_name: str,
        phone: str,
        address: str,
        total_price: Decimal,
    ) -> OrderModel:
        data = await self.connection.insert_and_fetchone(
            sql=f"""
                INSERT INTO orders_order
                    (client_id, full_name, phone, address, status, total_price, created_at, updated_at)
                VALUES (%s, %s, %s, %s, 'pending', %s, NOW(), NOW())
                RETURNING {_ORDER_COLS}
            """,
            params=(client_id, full_name, phone, address, total_price),
        )
        return data.to_model(OrderModel, raise_if_empty=True)

    async def get_active(self) -> list[OrderModel]:
        data = await self.connection.fetchmany(
            sql=f"""
                SELECT {_ORDER_COLS} FROM orders_order
                WHERE status IN ('pending', 'paid', 'processing', 'shipped')
                ORDER BY created_at DESC
                LIMIT 50
            """,
        )
        return data.to_models(OrderModel) or []

    async def get_by_id(self, *, order_id: int) -> OrderModel | None:
        data = await self.connection.fetchone(
            sql=f"SELECT {_ORDER_COLS} FROM orders_order WHERE id = %s",
            params=(order_id,),
        )
        if data.is_empty():
            return None
        return data.to_model(OrderModel)

    async def update_status(self, *, order_id: int, status: str, expected_old_status: str) -> None:
        from app.infrastructure.database.exceptions import StateConflictError

        rows = await self.connection.execute(
            sql="UPDATE orders_order SET status = %s, updated_at = NOW() WHERE id = %s AND status = %s",
            params=(status, order_id, expected_old_status),
        )
        if rows == 0:
            raise StateConflictError(
                f"Order {order_id} status cannot be updated from '{expected_old_status}' to '{status}' "
                "because the current status in DB has changed."
            )

    async def get_items(self, *, order_id: int) -> list[OrderItemModel]:
        data = await self.connection.fetchmany(
            sql="SELECT id, order_id, product_name, price, quantity FROM orders_orderitem WHERE order_id = %s",
            params=(order_id,),
        )
        return data.to_models(OrderItemModel) or []

    async def add_item(
        self,
        *,
        order_id: int,
        product_id: int,
        product_name: str,
        price: Decimal,
        quantity: int,
    ) -> None:
        await self.connection.execute(
            sql="""
                INSERT INTO orders_orderitem (order_id, product_id, product_name, price, quantity)
                VALUES (%s, %s, %s, %s, %s)
            """,
            params=(order_id, product_id, product_name, price, quantity),
        )
