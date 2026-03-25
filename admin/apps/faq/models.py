from django.db import models


class FAQItem(models.Model):
    question = models.CharField(max_length=500, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ["pk"]

    def __str__(self) -> str:
        return self.question
