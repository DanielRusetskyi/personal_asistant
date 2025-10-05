import logging
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Note
from preferences.models import UserSettings

from .push import send_web_push_to_user


task_logger = logging.getLogger("noteapp.tasks")


def user_push_enabled(user):
    prefs = getattr(user, "prefs", None)
    return bool(prefs and prefs.push_enabled)


@shared_task
def send_note_reminder(note_id):
    note = Note.objects.get(pk=note_id)

    send_mail(
        subject="Нагадування",
        message=note.description or "Нагадування.",
        from_email=None,
        recipient_list=[note.user.email],
        fail_silently=True,
    )
    task_logger.debug("Email sent: note_id=%s user_id=%s", note.id, note.user_id)

    if not UserSettings.objects.filter(user=note.user, push_enabled=True).exists():
        return 0, 0
    # Web Push тільки якщо увімкнено
    # if user_push_enabled(note.user):
    #     from .push import send_web_push_to_user

    group = f"user_{note.user_id}"
    payload = {
        "title": "Нагадування про завдання",
        "message": note.description or "Нагадування",
        "note_id": note.id,
        "url": f"/noteapp/{note.id}/",
    }
    async_to_sync(get_channel_layer().group_send)(group, {"type": "notify", "payload": payload})
    task_logger.debug("WS pushed: group=%s payload=%s", group, payload)

    send_web_push_to_user(note.user, payload, ttl=300, urgency="normal")

