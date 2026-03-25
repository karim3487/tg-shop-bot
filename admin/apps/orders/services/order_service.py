from django.db import transaction

from cart.models import CartItem
from clients.models import Client
from orders.models import Order, OrderItem
from orders.services.notifications import publish_new_order
from api.exceptions import OrderAlreadyProcessingError, OrderNotFoundError, OrderStatusConflictError


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_from_cart(
        client: Client, full_name: str, address: str, phone: str | None = None
    ) -> Order:
        """
        Create a new order from the client's current cart items.
        Wraps logic in transaction.atomic and uses bulk_create (Step 7).
        """
        cart_items = list(
            CartItem.objects.select_for_update()
            .filter(client=client)
            .select_related("product")
        )
        if not cart_items:
            raise OrderAlreadyProcessingError("Cart is empty or order is already processing")

        # Calculate total using prices at the time of order
        total = sum(item.product.price * item.quantity for item in cart_items)

        # Create the order
        order = Order.objects.create(
            client=client,
            full_name=full_name,
            phone=phone or client.phone or "",
            address=address,
            total_price=total,
        )

        # Bulk create order items (Step 6/7)
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity,
                )
                for cart_item in cart_items
            ]
        )

        # Clear the cart
        CartItem.objects.filter(client=client).delete()

        # Trigger background task on commit (Step 1)
        def safe_publish():
            try:
                publish_new_order.delay(order.pk)
            except Exception as e:
                # Log the error but don't crash the request—the order is already committed
                import logging
                logging.getLogger(__name__).error(f"Failed to publish new order #{order.pk} to RQ: {e}")

        transaction.on_commit(safe_publish)

        return order

    @staticmethod
    @transaction.atomic
    def mark_as_paid(order_id: int, client: Client) -> Order:
        """
        Mark order as paid by client. Gated to 'pending' -> 'paid' transition only.
        """
        from orders.services.notifications import notify_order_status

        try:
            order = Order.objects.select_for_update().get(pk=order_id, client=client)
        except Order.DoesNotExist:
            raise OrderNotFoundError("Order not found")

        if order.status != "pending":
            raise OrderStatusConflictError(f"Cannot mark order as paid: current status is {order.status}")

        order.status = "paid"
        order.save()

        # Notify user (background task)
        def safe_notify():
            try:
                notify_order_status.delay(client.telegram_id, order.pk, "paid")
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to notify status for order #{order.pk}: {e}")

        transaction.on_commit(safe_notify)
        return order
