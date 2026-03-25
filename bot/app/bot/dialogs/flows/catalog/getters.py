from aiogram_dialog import DialogManager

from app.infrastructure.database.db import DB


async def get_categories(dialog_manager: DialogManager, db: DB, **kwargs) -> dict:
    cats = await db.catalog.get_root_categories()
    return {"categories": [(c.name, str(c.id)) for c in cats]}


async def get_subcategories(dialog_manager: DialogManager, db: DB, **kwargs) -> dict:
    parent_id = int(dialog_manager.dialog_data["parent_category_id"])
    category = await db.catalog.get_category(category_id=parent_id)
    subcats = await db.catalog.get_subcategories(parent_id=parent_id)
    return {
        "title": category.name if category else "",
        "subcategories": [(c.name, str(c.id)) for c in subcats],
    }


async def get_products(dialog_manager: DialogManager, db: DB, **kwargs) -> dict:
    category_id = int(dialog_manager.dialog_data["category_id"])
    category = await db.catalog.get_category(category_id=category_id)
    products = await db.catalog.get_products(category_id=category_id)
    total = await db.catalog.count_products(category_id=category_id)
    return {
        "title": category.name if category else "",
        "products": [(p.name, str(p.id)) for p in products],
        "total": total,
    }


async def get_product(dialog_manager: DialogManager, db: DB, **kwargs) -> dict:
    product_id = int(dialog_manager.dialog_data["product_id"])
    product = await db.catalog.get_product(product_id=product_id)
    image_path: str | None = dialog_manager.dialog_data.get("image_path")
    photo_count: int = dialog_manager.dialog_data.get("photo_count", 0)
    if not product:
        return {"name": "Не найдено", "description": "", "price": "0",
                "image_path": None, "photo_count": 0, "has_more_photos": False}
    return {
        "name": product.name,
        "description": product.description,
        "price": str(product.price),
        "image_path": image_path,
        "photo_count": photo_count,
        "has_more_photos": photo_count > 1,
    }
