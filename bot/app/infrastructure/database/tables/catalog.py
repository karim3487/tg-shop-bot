from app.infrastructure.database.connection.base import BaseConnection
from app.infrastructure.database.models.catalog import CategoryModel, ProductImageModel, ProductModel
from app.infrastructure.database.tables.base import BaseTable

PRODUCTS_PER_PAGE = 5


class CatalogTable(BaseTable):
    __tablename__ = "catalog"

    def __init__(self, connection: BaseConnection):
        self.connection = connection

    async def get_root_categories(self) -> list[CategoryModel]:
        data = await self.connection.fetchmany(
            sql="SELECT id, name, parent_id, is_active FROM catalog_category WHERE parent_id IS NULL AND is_active = TRUE ORDER BY name",
        )
        return data.to_models(CategoryModel) or []

    async def get_subcategories(self, *, parent_id: int) -> list[CategoryModel]:
        data = await self.connection.fetchmany(
            sql="SELECT id, name, parent_id, is_active FROM catalog_category WHERE parent_id = %s AND is_active = TRUE ORDER BY name",
            params=(parent_id,),
        )
        return data.to_models(CategoryModel) or []

    async def get_category(self, *, category_id: int) -> CategoryModel | None:
        data = await self.connection.fetchone(
            sql="SELECT id, name, parent_id, is_active FROM catalog_category WHERE id = %s",
            params=(category_id,),
        )
        return data.to_model(CategoryModel)

    async def count_products(self, *, category_id: int) -> int:
        data = await self.connection.fetchone(
            sql="""
                SELECT COUNT(*) AS count
                FROM catalog_product p
                JOIN catalog_category c ON c.id = p.category_id
                WHERE (p.category_id = %s OR c.parent_id = %s) AND p.is_active = TRUE
            """,
            params=(category_id, category_id),
        )
        return int(data.data.get("count", 0)) if data else 0

    async def get_products(
        self, *, category_id: int, page: int = 0
    ) -> list[ProductModel]:
        offset = page * PRODUCTS_PER_PAGE
        data = await self.connection.fetchmany(
            sql="""
                SELECT p.id, p.name, p.description, p.price, p.category_id, p.is_active
                FROM catalog_product p
                JOIN catalog_category c ON c.id = p.category_id
                WHERE (p.category_id = %s OR c.parent_id = %s) AND p.is_active = TRUE
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """,
            params=(category_id, category_id, PRODUCTS_PER_PAGE, offset),
        )
        return data.to_models(ProductModel) or []

    async def get_product(self, *, product_id: int) -> ProductModel | None:
        data = await self.connection.fetchone(
            sql="SELECT id, name, description, price, category_id, is_active FROM catalog_product WHERE id = %s AND is_active = TRUE",
            params=(product_id,),
        )
        return data.to_model(ProductModel)

    async def get_product_images(self, *, product_id: int) -> list[ProductImageModel]:
        data = await self.connection.fetchmany(
            sql='SELECT id, product_id, image, "order" FROM catalog_productimage WHERE product_id = %s ORDER BY "order"',
            params=(product_id,),
        )
        return data.to_models(ProductImageModel) or []
