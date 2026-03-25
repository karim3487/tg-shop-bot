from django.contrib import admin

from .models import FAQItem


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("question", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")
    list_editable = ("is_active",)
