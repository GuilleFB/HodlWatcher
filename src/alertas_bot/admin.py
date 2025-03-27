from django.contrib import admin

from .models import Configuracion


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ["user", "user_telegram", "image"]
    search_fields = ["user__username"]
    readonly_fields = ["user"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "user_telegram",
                    "image",
                )
            },
        ),
    )
