# noteapp/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Note


@shared_task
def send_note_reminder(note_id):
    note = Note.objects.get(pk=note_id)
    # приклад: надсилаємо email (зроби свою дію — пуш, вебсокет, т.п.)
    send_mail(
        subject="Нагадування",
        message=note.description or "Нагадування.",
        from_email=None,
        recipient_list=[note.user.email],
        fail_silently=True,
    )

