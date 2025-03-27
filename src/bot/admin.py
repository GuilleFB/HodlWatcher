from django.contrib import admin

from .models import UsuarioTelegram


@admin.register(UsuarioTelegram)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "username", "rate_fee")
    search_fields = ("chat_id", "username", "rate_fee")
    list_filter = ("username",)
    ordering = ("chat_id", "username")
    fields = ("chat_id", "username", "rate_fee")
    readonly_fields = ("chat_id", "username")
    list_per_page = 50
    list_max_show_all = 100
