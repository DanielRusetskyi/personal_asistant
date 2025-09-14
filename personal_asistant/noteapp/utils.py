from datetime import datetime

from django.utils import timezone
from django.core.paginator import Paginator
from .models import Note
from .forms import NoteForm


def get_day_context(request, day: datetime.date):
    today = timezone.localdate()
    form_disabled = day < today

    notes = Note.objects.filter(doe_date=day, user=request.user).order_by('due_time')
    referer = request.META.get('HTTP_REFERER')

    context = {
            'notes': notes,
            'day': day,
            'form_disabled': form_disabled,
       }
    if referer:
        context['return_url'] = referer

    return context
