from django.contrib import admin, messages

from .models import Broadcast


def send_broadcast(modeladmin, request, queryset):
    allowed = queryset.filter(status__in=[Broadcast.Status.DRAFT, Broadcast.Status.READY])
    count = allowed.update(status=Broadcast.Status.READY)
    messages.success(request, f"Поставлено в очередь: {count} рассылок.")

send_broadcast.short_description = "Запустить рассылку"


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ("pk", "status", "sent_count", "error_count", "created_at", "sent_at")
    list_filter = ("status",)
    readonly_fields = ("sent_count", "error_count", "sent_at")
    actions = [send_broadcast]
    fieldsets = (
        (None, {"fields": ("text", "image")}),
        ("Результат", {"fields": ("status", "sent_count", "error_count", "sent_at")}),
    )
