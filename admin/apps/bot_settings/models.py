from django.core.exceptions import ValidationError
from django.db import models


class RequiredChannel(models.Model):
    channel_id = models.CharField(
        max_length=100,
        verbose_name="ID канала",
        help_text="@username или -100xxxxxxxxxx",
    )
    title = models.CharField(max_length=255, verbose_name="Название канала")
    invite_link = models.URLField(null=True, blank=True, verbose_name="Ссылка для вступления")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Обязательный канал"
        verbose_name_plural = "Обязательные каналы"

    def __str__(self) -> str:
        return f"{self.title} ({self.channel_id})"


class BotConfigQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        raise ValidationError("This configuration cannot be deleted.")


class BotConfigManager(models.Manager):
    def get_queryset(self):
        return BotConfigQuerySet(self.model, using=self._db)


class BotConfig(models.Model):
    admin_chat_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="ID admin-чата",
        help_text="ID Telegram-группы для уведомлений о заказах",
    )

    objects = BotConfigManager()

    class Meta:
        verbose_name = "Настройки бота"
        verbose_name_plural = "Настройки бота"

    def __str__(self) -> str:
        return "Настройки бота"

    @classmethod
    def load(cls):
        """Safely retrieve or create the configuration singleton (PK=1)."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        # Singleton — всегда только одна запись
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("This configuration cannot be deleted.")
