from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает оплаты"
        PAID = "paid", "Оплачен"
        PROCESSING = "processing", "В обработке"
        SHIPPED = "shipped", "Отправлен"
        DELIVERED = "delivered", "Доставлен"
        CANCELLED = "cancelled", "Отменён"

    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Клиент",
    )
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес доставки")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Статус",
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Заказ #{self.pk} — {self.client}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        verbose_name="Товар",
    )
    product_name = models.CharField(max_length=255, verbose_name="Название товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self) -> str:
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
