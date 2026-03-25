from django.contrib import admin

from .models import BotConfig, RequiredChannel


@admin.register(RequiredChannel)
class RequiredChannelAdmin(admin.ModelAdmin):
    list_display = ("title", "channel_id", "invite_link", "is_active")
    list_editable = ("is_active",)
    search_fields = ("title", "channel_id")


@admin.register(BotConfig)
class BotConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Telegram", {"fields": ("admin_chat_id",)}),
    )

    def has_add_permission(self, request):
        return not BotConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
