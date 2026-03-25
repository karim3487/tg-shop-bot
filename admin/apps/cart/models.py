from django.db import models


class CartItem(models.Model):
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Клиент",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Корзины"
        unique_together = ("client", "product")

    def __str__(self) -> str:
        return f"{self.client} — {self.product.name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity
