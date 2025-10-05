# preferences/models.py
from django.conf import settings
from django.db import models

THEMES = (("auto", "Auto"), ("light", "Light"), ("dark", "Dark"))


class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="settings")
    language = models.CharField(max_length=10, default="en")
    theme = models.CharField(max_length=10, choices=THEMES, default="auto")  # auto | light | dark
    compact_ui = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=False)                        # <-- нове поле
    extra = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings({self.user})"
