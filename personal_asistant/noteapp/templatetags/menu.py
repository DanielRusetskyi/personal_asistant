from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def main_menu(context):
    """
    Повертає список пунктів головного меню з урахуванням авторизації.
    """
    user = context.get("user")
    items = [
        {
            "key": "notebook",
            "label": "Notebook",
            "icon_img": "images/notebook_icon_2.png",
            "icon_emoji": "📋",
            "href": reverse("noteapp:notebook"),
            "auth_only": True,
        },
        {
            "key": "phonebook",
            "label": "Phonebook",
            "icon_img": "images/phonebook_icon_3.png",
            "icon_emoji": "📞",
            "href": "#",
            "auth_only": True,
        },
        # public
        {
            "key": "weather",
            "label": "Погода",
            "icon_img": "images/weather_icon.png",
            "icon_emoji": "🌦️",
            "href": reverse("weather"),
            "auth_only": False,
        },
        {
            "key": "rates",
            "label": "Курси",
            "icon_img": "images/exchange_icon.png",
            "icon_emoji": "💱",
            "href": "#",
            "auth_only": False,
        },
        {
            "key": "radio",
            "label": "Радіо",
            "icon_img": "images/radio_icon.png",
            "icon_emoji": "📻",
            "href": "#",
            "auth_only": False,
        },
    ]
    if user and user.is_authenticated:
        return items
    return [i for i in items if not i["auth_only"]]


@register.simple_tag(takes_context=True)
def notebook_submenu(context):
    """
    Одне джерело правди для всіх підпунктів Notebook з вашою логікою дат.
    Доступний і для мобільного, і для десктопу — просто рендеримо по-різному.
    """
    user = context.get("user")
    if not (user and user.is_authenticated):
        return []

    date_ = context.get("date_")
    year = context.get("year")
    month = context.get("month")
    selected_day = context.get("selected_day")

    # Календар: обираємо правильний URL залежно від наявних змінних
    if date_:
        calendar_href = reverse("noteapp:calendar", kwargs={"date_": date_})
    elif year and month:
        calendar_href = reverse("noteapp:calendar", kwargs={"year": year, "month": month})
    else:
        calendar_href = reverse("noteapp:calendar_current")

    # Сьогодні/обраний день
    from django.utils.timezone import now
    today = now().date().strftime("%Y-%m-%d")
    current_day = selected_day or today
    today_href = reverse("noteapp:notebook_by_date", args=[current_day])

    return [
        {
            "key": "calendar",
            "label": "Календар",
            "icon_img": "images/calendar_icon.png",
            "icon_emoji": "📆",
            "href": calendar_href,
        },
        {
            "key": "notebook_by_date",
            "label": "Сьогодні",
            "icon_img": "images/notebook_icon_today.png",
            "icon_emoji": "🗓️",
            "href": today_href,
        },
        {
            "key": "task_by_period",
            "label": "Завдання",
            "icon_img": "images/notebook_icon_between.png",
            "icon_emoji": "📋",
            "href": reverse("noteapp:task_by_period"),
        },
        {
            "key": "reminders",
            "label": "Нагадування",
            "icon_img": "images/reminder_icon.png",
            "icon_emoji": "⏰",
            "href": "#",
        },
        {
            "key": "settings",
            "label": "Налаштування",
            "icon_img": "images/settings_icon.png",
            "icon_emoji": "⚙️",
            "href": "#",
        },
        {
            "key": "back",
            "label": "Повернутися",
            "icon_img": "images/back_icon2.png",
            "icon_emoji": "🤖",
            "href": reverse("main"),
        },
    ]
