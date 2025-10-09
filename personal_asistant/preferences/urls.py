# preferences/urls.py
from django.urls import path
from . import views

app_name = "preferences"
urlpatterns = [
    path("", views.SettingsView.as_view(), name="settings"),
    path("language/", views.LanguagePageView.as_view(), name="language"),
    path("language/update/", views.UpdateLanguageView.as_view(), name="language_update"),
    path("update-theme/", views.UpdateThemeView.as_view(), name="update_theme"),
    path("update-compact/", views.UpdateCompactView.as_view(), name="update_compact"),
    path("push/update/", views.UpdatePushEnabledView.as_view(), name="push_update"),
]
