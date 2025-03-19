from django.contrib import admin

from .models import UsuarioTelegram


@admin.register(UsuarioTelegram)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "username")
    search_fields = ("chat_id", "username")
    list_filter = ("username",)
    ordering = ("chat_id",)
    fields = ("chat_id", "username")
    readonly_fields = ("chat_id",)
