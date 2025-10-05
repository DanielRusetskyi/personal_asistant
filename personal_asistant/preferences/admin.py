from django.contrib import admin
from .models import UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "language", "theme", "compact_ui", "push_enabled")
    search_fields = ("user__username", "user__email")
