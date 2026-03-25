from decimal import Decimal

from pydantic import BaseModel


class CategoryModel(BaseModel):
    id: int
    name: str
    parent_id: int | None = None
    is_active: bool = True


class ProductModel(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    category_id: int
    is_active: bool = True


class ProductImageModel(BaseModel):
    id: int
    product_id: int
    image: str  # relative path stored in DB, e.g. "products/product_1_0.jpg"
    order: int = 0
