import logging
from decimal import Decimal

from psycopg_pool import AsyncConnectionPool

from app.infrastructure.database.connection.psycopg_connection import PsycopgConnection
from app.infrastructure.database.db import DB
from app.infrastructure.database.models.order import OrderModel

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, db_pool: AsyncConnectionPool):
        self.db_pool = db_pool

    async def checkout(
        self,
        client_id: int,
        full_name: str,
        phone: str,
        address: str,
    ) -> OrderModel:
        """
        Atomically creates an order from the client's cart items.
        
        Steps:
        1. Start transaction
        2. Get cart items
        3. Create order
        4. Move items from cart to order
        5. Clear cart
        6. Commit transaction
        """
        async with self.db_pool.connection() as conn:
            # We use an explicit transaction block to ensure atomicity
            async with conn.transaction():
                connection = PsycopgConnection(conn)
                db = DB(connection)

                # 1. Get cart items
                cart_items = await db.cart.get_items(client_id=client_id)
                if not cart_items:
                    raise ValueError("Cart is empty")

                # 2. Calculate total
                total = sum(item.subtotal for item in cart_items)

                # 3. Create order
                order = await db.orders.create(
                    client_id=client_id,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    total_price=Decimal(str(total)),
                )

                # 4. Move items to order
                for item in cart_items:
                    await db.orders.add_item(
                        order_id=order.id,
                        product_id=item.product_id,
                        product_name=item.product_name,
                        price=item.product_price,
                        quantity=item.quantity,
                    )

                # 5. Clear cart
                await db.cart.clear(client_id=client_id)

                logger.info(
                    "Order #%s created for client %s (Total: %s)",
                    order.id, client_id, total
                )
                return order
