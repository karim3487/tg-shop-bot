from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active", "products_count")
    list_filter = ("is_active", "parent")
    search_fields = ("name",)
    list_editable = ("is_active",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("parent")
            .annotate(_products_count=Count("products"))
        )

    def products_count(self, obj):
        return getattr(obj, "_products_count", 0)

    products_count.short_description = "Товаров"
    products_count.admin_order_field = "_products_count"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "order", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;">', obj.image.url)
        return "—"
    preview.short_description = "Превью"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("name", "description")
    list_editable = ("price", "is_active")
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {"fields": ("name", "category", "is_active")}),
        ("Детали", {"fields": ("description", "price")}),
    )
