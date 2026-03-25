from django.db import models


class Client(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Пользователь"
        ADMIN = "admin", "Администратор"
        OWNER = "owner", "Владелец"

    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Username")
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Телефон")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER, verbose_name="Роль")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.first_name} (@{self.username}) [{self.telegram_id}]"

    @property
    def is_authenticated(self) -> bool:
        return self.is_active

    @property
    def full_name(self) -> str:
        parts = [self.first_name]
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts)

    @property
    def orders_count(self) -> int:
        return self.orders.count()

    @property
    def orders_total(self):
        from django.db.models import Sum
        return self.orders.aggregate(total=Sum("total_price"))["total"] or 0
