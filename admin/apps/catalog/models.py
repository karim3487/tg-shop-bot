from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        verbose_name="Родительская категория",
    )
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self) -> str:
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категория",
    )
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар",
    )
    image = models.ImageField(upload_to="products/", verbose_name="Изображение")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"
        ordering = ["order"]

    def __str__(self) -> str:
        return f"Фото #{self.pk} → {self.product.name}"
