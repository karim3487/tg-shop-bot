from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "full_name_display",
        "username_link",
        "phone",
        "role",
        "orders_count_display",
        "orders_total_display",
        "is_active",
        "created_at",
    )
    list_filter = ("role", "is_active")
    search_fields = ("first_name", "last_name", "username", "phone", "telegram_id")
    readonly_fields = ("telegram_id", "created_at", "orders_count_display", "orders_total_display")

    fieldsets = (
        ("Telegram", {"fields": ("telegram_id", "username", "first_name", "last_name")}),
        ("Контакты", {"fields": ("phone",)}),
        ("Статус", {"fields": ("role", "is_active", "created_at")}),
        ("Статистика", {"fields": ("orders_count_display", "orders_total_display")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                _orders_count=Count("orders"),
                _orders_total=Sum("orders__total_price"),
            )
        )

    def full_name_display(self, obj):
        return obj.full_name

    full_name_display.short_description = "Имя"

    def username_link(self, obj):
        if obj.username:
            return format_html(
                '<a href="https://t.me/{}" target="_blank">@{}</a>', obj.username, obj.username
            )
        return "—"

    username_link.short_description = "Username"

    def orders_count_display(self, obj):
        return getattr(obj, "_orders_count", 0)

    orders_count_display.short_description = "Заказов"
    orders_count_display.admin_order_field = "_orders_count"

    def orders_total_display(self, obj):
        total = getattr(obj, "_orders_total", 0) or 0
        return f"{total} ₽"

    orders_total_display.short_description = "Сумма заказов"
    orders_total_display.admin_order_field = "_orders_total"
