# preferences/services.py
from django.utils.translation import activate
from .models import UserSettings


def get_or_create_user_settings(user):
    us, _ = UserSettings.objects.get_or_create(user=user)
    return us


def set_language(user, lang_code):
    us = get_or_create_user_settings(user)
    if us.language != lang_code:
        us.language = lang_code
        us.save(update_fields=["language"])
    activate(lang_code)


def set_theme(user, theme):
    us = get_or_create_user_settings(user)
    us.theme = theme
    us.save(update_fields=["theme"])


def set_compact(user, value: bool):
    us = get_or_create_user_settings(user)
    us.compact_ui = bool(value)
    us.save(update_fields=["compact_ui"])


def set_push_enabled(user, value: bool):
    us = get_or_create_user_settings(user)
    us.push_enabled = bool(value)
    us.save(update_fields=["push_enabled"])
