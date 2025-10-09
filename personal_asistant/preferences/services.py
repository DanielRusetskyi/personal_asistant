# preferences/services.py
from django.conf import settings
from django.utils.translation import activate
from .models import UserSettings
from urllib.parse import urlsplit, urlunsplit

LANG_CODES = {code for code, _ in settings.LANGUAGES}


def get_or_create_user_settings(user):
    us, _ = UserSettings.objects.get_or_create(user=user)
    return us


def _relocalize_url(original_url: str, target_lang: str) -> str:
    """
    Перекладає абсолютний або відносний URL у target_lang з урахуванням i18n_patterns
    та prefix_default_language=False (дефолтна мова без префікса).
    """
    parts = urlsplit(original_url)  # працює і для '/uk/...' і для 'http://host/uk/...'
    path = parts.path or "/"

    # Зняти поточний префікс мови, якщо є
    seg = path.lstrip("/").split("/", 1)
    if seg and seg[0] in LANG_CODES:
        rest = seg[1] if len(seg) > 1 else ""
    else:
        rest = path.lstrip("/")

    # Зібрати новий шлях із цілевою мовою
    if (target_lang == settings.LANGUAGE_CODE) and getattr(settings, "PREFIX_DEFAULT_LANGUAGE", False) is False:
        # дефолтна мова без префікса
        new_path = "/" + (rest or "")
    else:
        new_path = f"/{target_lang}/" + (rest or "")

    # Упорядкувати подвійні слеші
    new_path = "/" + new_path.lstrip("/")

    return urlunsplit((parts.scheme, parts.netloc, new_path, parts.query, parts.fragment))


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
