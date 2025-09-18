from django.contrib import admin
from .models import Station


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "is_active", "order")
    list_filter = ("is_active", "country")
    search_fields = ("name", "tags", "country")
    prepopulated_fields = {"slug": ("name",)}
