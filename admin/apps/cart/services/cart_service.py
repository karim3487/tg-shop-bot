from decimal import Decimal

from django.db.models import F, QuerySet, Sum

from cart.models import CartItem
from catalog.models import Product
from clients.models import Client
from api.exceptions import InvalidCartQuantityError


class CartService:
    @staticmethod
    def get_items(client: Client) -> QuerySet[CartItem]:
        """Get all items in the client's cart with related product data."""
        return (
            CartItem.objects.filter(client=client)
            .select_related("product__category")
            .prefetch_related("product__images")
        )

    @staticmethod
    def calculate_total(client: Client) -> Decimal:
        """
        Calculate total price of all items in the cart.
        Uses SQL aggregation for efficiency (Step 10).
        """
        result = CartItem.objects.filter(client=client).aggregate(
            total=Sum(F("product__price") * F("quantity"))
        )
        return result["total"] or Decimal("0.00")

    @staticmethod
    def add_or_update_item(client: Client, product: Product, quantity: int) -> CartItem:
        """Add a product to the cart or update its quantity if it already exists."""
        if quantity <= 0:
            raise InvalidCartQuantityError("Cart quantity must be greater than zero.")
            
        item, created = CartItem.objects.get_or_create(
            client=client,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity = quantity
            item.save(update_fields=["quantity"])
        return item

    @staticmethod
    def remove_item(client: Client, item_id: int | None = None) -> None:
        """Remove a specific item or clear the entire cart for a client."""
        qs = CartItem.objects.filter(client=client)
        if item_id:
            qs = qs.filter(pk=item_id)
        qs.delete()
