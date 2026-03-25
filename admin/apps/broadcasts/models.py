from django.db import models


class Broadcast(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        READY = "ready", "Готово к отправке"
        SENDING = "sending", "Отправляется"
        SENT = "sent", "Отправлено"

    text = models.TextField(verbose_name="Текст")
    image = models.ImageField(upload_to="broadcasts/", null=True, blank=True, verbose_name="Изображение")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Статус",
    )
    sent_count = models.PositiveIntegerField(default=0, verbose_name="Доставлено")
    error_count = models.PositiveIntegerField(default=0, verbose_name="Ошибок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Отправлена")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Рассылка #{self.pk} [{self.get_status_display()}]"
