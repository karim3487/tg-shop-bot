from decimal import Decimal

from pydantic import BaseModel


class CartItemModel(BaseModel):
    id: int
    client_id: int
    product_id: int
    quantity: int
    product_name: str
    product_price: Decimal
    product_image: str | None = None

    @property
    def subtotal(self) -> Decimal:
        return self.product_price * self.quantity
