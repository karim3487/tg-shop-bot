from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderModel(BaseModel):
    id: int
    client_id: int
    full_name: str
    phone: str
    address: str
    status: str
    total_price: Decimal
    created_at: datetime


class OrderItemModel(BaseModel):
    id: int
    order_id: int
    product_name: str
    price: Decimal
    quantity: int

    @property
    def subtotal(self) -> Decimal:
        return self.price * self.quantity
