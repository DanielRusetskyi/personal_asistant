from datetime import datetime

from django.utils import timezone
from django.core.paginator import Paginator
from .models import Note


def get_day_context(request, date):
    day = datetime.strptime(date, "%Y-%m-%d").date()
    today = timezone.localdate()
    form_disabled = day < today

    notes_list = Note.objects.filter(doe_date=day, user=request.user).order_by('due_time')
    paginator = Paginator(notes_list, 7)
    page_number = request.GET.get('page')
    notes = paginator.get_page(page_number)

    return {
        'notes': notes,
        'day': day,
        'form_disabled': form_disabled,
        'page_number': page_number,
    }
