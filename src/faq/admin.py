# admin.py
from django.contrib import admin
from .models import FAQ, FAQCategory


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")
    prepopulated_fields = {"slug": ("question",)}
    list_editable = ("order", "is_active")
    fieldsets = (
        (None, {"fields": ("question", "answer", "slug")}),
        ("Opciones", {"fields": ("order", "is_active")}),
    )


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
