from django import template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.simple_tag(takes_context=True)
def main_menu(context):
    """
    Головне меню з урахуванням авторизації. Підписи локалізовані (_()).
    """
    user = context.get("user")
    items = [
        {
            "key": "notebook",
            "label": _("Notebook"),
            "icon_img": "images/notebook_icon_2.png",
            "icon_emoji": "📋",
            "href": reverse("noteapp:notebook"),
            "auth_only": True,
        },
        {
            "key": "phonebook",
            "label": _("Phonebook"),
            "icon_img": "images/phonebook_icon_3.webp",
            "icon_emoji": "📞",
            "href": "#",
            "auth_only": True,
        },
        {
            "key": "settings",
            "label": _("Settings"),
            "icon_img": "images/settings_icon.webp",
            "icon_emoji": "⚙️",
            "href": reverse("preferences:settings"),
            "auth_only": True,
        },
        {
            "key": "chat",
            "label": _("Chat"),
            "icon_img": "images/phone_icon.png",  # або нова іконка
            "icon_emoji": "💬",
            "href": reverse("chat:home"),
            "auth_only": True,
        },
        # public
        {
            "key": "weather",
            "label": _("Weather"),
            "icon_img": "images/weather_icon.webp",
            "icon_emoji": "🌦️",
            "href": reverse("additional:weather"),
            "auth_only": False,
        },
        {
            "key": "rates",
            "label": _("Rates"),
            "icon_img": "images/exchange_icon.png",
            "icon_emoji": "💱",
            "href": reverse("additional:rates_page"),
            "auth_only": False,
        },
        {
            "key": "radio",
            "label": _("Radio"),
            "icon_img": "images/radio_icon.webp",
            "icon_emoji": "📻",
            "href": reverse("additional:radio"),
            "auth_only": False,
        },
    ]
    if user and user.is_authenticated:
        return items
    return [i for i in items if not i["auth_only"]]


@register.simple_tag(takes_context=True)
def notebook_submenu(context):
    """
    Підменю Notebook (локалізовані label).
    """
    user = context.get("user")
    if not (user and user.is_authenticated):
        return []

    date_ = context.get("date_")
    year = context.get("year")
    month = context.get("month")
    selected_day = context.get("selected_day")

    if date_:
        calendar_href = reverse("noteapp:calendar", kwargs={"date_": date_})
    elif year and month:
        calendar_href = reverse("noteapp:calendar", kwargs={"year": year, "month": month})
    else:
        calendar_href = reverse("noteapp:calendar_current")

    from django.utils.timezone import now
    today = now().date().strftime("%Y-%m-%d")
    current_day = selected_day or today
    today_href = reverse("noteapp:notebook_by_date", args=[current_day])

    return [
        {
            "key": "calendar",
            "label": _("Calendar"),
            "icon_img": "images/calendar_icon.png",
            "icon_emoji": "📆",
            "href": calendar_href,
        },
        {
            "key": "notebook_by_date",
            "label": _("Today"),
            "icon_img": "images/notebook_icon_today.png",
            "icon_emoji": "🗓️",
            "href": today_href,
        },
        {
            "key": "task_by_period",
            "label": _("Tasks"),
            "icon_img": "images/notebook_icon_between.png",
            "icon_emoji": "📋",
            "href": reverse("noteapp:task_by_period"),
        },
        {
            "key": "reminders",
            "label": _("Reminders"),
            "icon_img": "images/reminder_icon.webp",
            "icon_emoji": "⏰",
            "href": "#",
        },
        {
            "key": "back",
            "label": _("Back"),
            "icon_img": "images/back_icon2.png",
            "icon_emoji": "🤖",
            "href": reverse("main"),
        },
    ]


@register.simple_tag(takes_context=True)
def header_menu(context):
    """
    Елементи хедера. label локалізовані.
    """
    user = context.get("user")
    items = [
        {
            "key": "search",
            "label": _("Search"),
            "icon_img": "images/search_icon.webp",
            "icon_emoji": "🔎",
            "type": "action",
            "action": "open_search",
        },
    ]

    if user and user.is_authenticated:
        items += [
            {
                "key": "profile",
                "label": _("Profile"),
                "icon_img": "images/profile_icon.webp",
                "icon_emoji": "👤",
                "type": "link",
                "href": reverse("accounts:profile"),
            },
            {
                "key": "logout",
                "label": _("Logout"),
                "icon_img": "images/logout_icon.png",
                "icon_emoji": "🚪",
                "type": "post",
                "url": reverse("accounts:logout"),
            },
        ]
    else:
        items += [
            {
                "key": "login",
                "label": _("Sign in"),
                "icon_img": "images/login_icon.png",
                "icon_emoji": "🔐",
                "type": "link",
                "href": reverse("accounts:login"),
            },
            {
                "key": "registration",
                "label": _("Sign up"),
                "icon_img": "images/register_icon.webp",
                "icon_emoji": "📝",
                "type": "link",
                "href": reverse("accounts:registration"),
            },
        ]

    return items


@register.simple_tag(takes_context=True)
def settings_submenu(context):
    """
    Підменю налаштувань. ВАЖЛИВО: посилання на Language має вести на сторінку (GET),
    тобто 'preferences:language', а не на POST 'language_update'.
    """
    user = context.get("user")
    if not (user and user.is_authenticated):
        return []
    items = [
        {
            "key": "push_update",
            "label": _("Push"),
            "icon_img": "images/phonebook_icon_3.webp",
            "icon_emoji": "🔔",
            "href": reverse("preferences:push_update"),
        },
        {
            "key": "language",
            "label": _("Language"),
            "icon_img": "images/phonebook_icon_3.png",
            "icon_emoji": "🌐",
            "href": reverse("preferences:language"),  # <-- фікс сюди
        },
        {
            "key": "appearance",
            "label": _("Appearance"),
            "icon_img": "images/phonebook_icon_3.png",
            "icon_emoji": "🎨",
            "href": "#privacy",
        },
        {
            "key": "privacy",
            "label": _("Privacy"),
            "icon_img": "images/phonebook_icon_3.png",
            "icon_emoji": "🔒",
            "href": "#privacy",
        },
        {
            "key": "account",
            "label": _("Account"),
            "icon_img": "images/phonebook_icon_3.png",
            "icon_emoji": "👤",
            "href": "#account",
        },
        {
            "key": "back",
            "label": _("Back"),
            "icon_img": "images/back_icon3.png",
            "icon_emoji": " ⬅ ",
            "href": reverse("main"),
        },
    ]
    return items
