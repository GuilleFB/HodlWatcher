from django.contrib import admin

from .models import Configuracion


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ("rate_fee",)
