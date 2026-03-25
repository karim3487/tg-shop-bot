import io

import openpyxl
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Order, OrderItem
from .services.notifications import notify_order_status


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "price", "quantity", "subtotal_display")
    can_delete = False

    def subtotal_display(self, obj):
        return f"{obj.subtotal} ₽"
    subtotal_display.short_description = "Сумма"

    def has_add_permission(self, request, obj=None):
        return False


def export_to_excel(modeladmin, request, queryset):
    """Экспорт оплаченных заказов в Excel."""
    paid = queryset.filter(status=Order.Status.PAID).prefetch_related("items", "client")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Оплаченные заказы"

    headers = ["ID", "Клиент", "Телефон", "ФИО", "Адрес", "Сумма", "Дата"]
    ws.append(headers)

    for order in paid:
        ws.append([
            order.pk,
            str(order.client),
            order.phone,
            order.full_name,
            order.address,
            float(order.total_price),
            order.created_at.strftime("%d.%m.%Y %H:%M"),
        ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    response = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="orders.xlsx"'
    return response

export_to_excel.short_description = "Экспорт оплаченных заказов в Excel"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "client", "full_name", "status_badge", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "phone", "client__username", "client__telegram_id")
    readonly_fields = ("client", "full_name", "phone", "address", "total_price", "created_at", "updated_at")
    inlines = [OrderItemInline]
    actions = [export_to_excel]

    fieldsets = (
        ("Клиент", {"fields": ("client", "full_name", "phone")}),
        ("Заказ", {"fields": ("address", "total_price", "status")}),
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )

    def status_badge(self, obj):
        colors = {
            "pending": "#f59e0b",
            "paid": "#10b981",
            "processing": "#3b82f6",
            "shipped": "#8b5cf6",
            "delivered": "#22c55e",
            "cancelled": "#ef4444",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_badge.short_description = "Статус"

    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data:
            super().save_model(request, obj, form, change)
            try:
                notify_order_status.delay(
                    telegram_id=obj.client.telegram_id,
                    order_id=obj.pk,
                    status=obj.status,
                )
                messages.success(request, f"Уведомление отправлено в очередь для {obj.client}")
            except Exception as e:
                messages.warning(request, f"Заказ сохранён, но уведомление не отправлено: {e}")
        else:
            super().save_model(request, obj, form, change)
