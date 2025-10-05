# preferences/urls.py
from django.urls import path
from .views import (
    SettingsView, UpdateLanguageView, UpdateThemeView, UpdateCompactView, UpdatePushEnabledView, LanguagePageView
)

app_name = "preferences"
urlpatterns = [
    path("", SettingsView.as_view(), name="settings"),
    path("language/", LanguagePageView.as_view(), name="language"),
    path("language/update/", UpdateLanguageView.as_view(), name="language_update"),
    path("update-theme/", UpdateThemeView.as_view(), name="update_theme"),
    path("update-compact/", UpdateCompactView.as_view(), name="update_compact"),
    path("push/update/", UpdatePushEnabledView.as_view(), name="push_update"),
]
