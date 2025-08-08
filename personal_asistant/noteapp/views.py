import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import UpdateView, DeleteView, TemplateView
from django.views import View
from django.core.paginator import Paginator
from .models import Note
from .forms import NoteForm
from datetime import datetime
from django.shortcuts import render, redirect
from datetime import date, timedelta
from django.utils import timezone
from django.contrib import messages
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
import calendar as calmod

from .services import create_note_for_user
from .utils import get_day_context


@require_POST
def toggle_task_status(request):
    data = json.loads(request.body)
    task_id = data.get("task_id")
    done = data.get("done")

    try:
        note = Note.objects.get(id=task_id, user=request.user)
        note.done = done
        note.save()
        return JsonResponse({"success": True})
    except Note.DoesNotExist:
        return JsonResponse({"success": False, "error": "Note not found"}, status=404)


def tasks_by_period_view(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    tasks_by_day = {}

    if start and end:
        try:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)

            if start_date > end_date:
                messages.warning(request, "Початкова дата не може бути пізніше за кінцеву.")
            else:
                notes = Note.objects.filter(
                    user=request.user,
                    doe_date__range=[start_date, end_date]
                ).order_by("doe_date", "due_time")

                from collections import defaultdict
                grouped = defaultdict(list)
                for note in notes:
                    grouped[note.doe_date].append(note)

                tasks_by_day = dict(grouped)
        except ValueError:
            messages.warning(request, "Невірний формат дати.")

    return render(request, "noteapp/tasks_by_period.html", {
        "tasks_by_day": tasks_by_day,
        "start_date": start,
        "end_date": end,
        "active_page": "task_by_period",
        "active_menu": "notebook"
    })


def notebook(request):
    return render(request, 'noteapp/notebook.html', {
        "active_page": "notebook",
        "active_menu": "notebook"
    })


def calendar_view(request, date_=None, year=None, month=None):
    today = timezone.localdate()
    selected_day = None

    # Якщо передали date_ у вигляді шляху /calendar/YYYY-MM-DD/
    if date_ and str(date_).lower() != 'none':
        try:
            selected_day = datetime.strptime(date_, "%Y-%m-%d").date()
            year, month = selected_day.year, selected_day.month
        except ValueError:
            # Некоректна дата → редірект на поточний місяць (щоб не падати)
            return redirect('noteapp:calendar_current')

    # Якщо рік/місяць не задані, візьми їх з selected_day або today
    if year is None or month is None:
        base = selected_day or today
        year, month = base.year, base.month

    # Налаштування календаря
    calmod.setfirstweekday(calmod.MONDAY)
    cal = calmod.Calendar()
    month_days = cal.monthdatescalendar(year, month)

    # Навігація по місяцях
    prev_year, prev_month = (year, month - 1) if month > 1 else (year - 1, 12)
    next_year, next_month = (year, month + 1) if month < 12 else (year + 1, 1)

    context = {
        "calendar_weeks": month_days,
        "current_date": date(year, month, 1),
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "selected_day": selected_day,  # для підсвітки
        "today": today,
        "active_page": "calendar",
        "active_menu": "notebook",
    }
    return render(request, "noteapp/calendar.html", context)


def task(request):

    return render(request, 'noteapp/task.html', {
        'active_page': 'calendar',
        'active_menu': 'notebook'
    })


class DayTaskView_(LoginRequiredMixin, View):
    def get(self, request, date=None):
        if not date:
            day = timezone.localdate()
            date = day.strftime('%Y-%m-%d')  # для виклику get_day_context
        else:
            day = datetime.strptime(date, "%Y-%m-%d").date()

        context = get_day_context(request, date)

        # Додаткові змінні (навігація між днями, активна сторінка)
        context.update({
            'active_page': 'day_tasks',
            'active_menu': 'notebook',
            'prev_day': (day - timedelta(days=1)).strftime('%Y-%m-%d'),
            'next_day': (day + timedelta(days=1)).strftime('%Y-%m-%d'),
            'day': context['day']
        })

        return render(request, 'noteapp/day_tasks.html', context)


class DayTaskView(LoginRequiredMixin, View):
    def get(self, request, date=None):
        if not date:
            day = timezone.localdate()
            # date_ = day.strftime('%Y-%m-%d')  # для виклику get_day_context
        else:
            day = datetime.strptime(date, "%Y-%m-%d").date()

        context = get_day_context(request, day)
        context['form'] = NoteForm(initial={'doe_date': context['day']})
        context['active_page'] = 'notebook_by_date'
        context['active_menu'] = 'notebook'
        context['prev_day'] = (day - timedelta(days=1)).strftime('%Y-%m-%d')
        context['next_day'] = (day + timedelta(days=1)).strftime('%Y-%m-%d')
        context['today'] = day
        context['year'] = day.year
        context['month'] = day.month

        return render(request, 'noteapp/notebook_by_date.html', context)

    def post(self, request, date):
        form = NoteForm(request.POST)
        page = request.POST.get('page')
        if form.is_valid():
            note_data = form.cleaned_data
            note_data["doe_date"] = datetime.strptime(date, "%Y-%m-%d").date()
            create_note_for_user(request.user, note_data)

            url = reverse('noteapp:notebook_by_date', kwargs={'date': date})
            if page:
                return redirect(f"{url}?page={page}")
            return redirect(url)
        day = datetime.strptime(date, "%Y-%m-%d").date()
        notes = Note.objects.filter(doe_date=day, user=request.user)
        return render(request, 'noteapp/notebook_by_date.html', {
            'notes': notes,
            'form': form,
            'day': day,
            'year': day.year,
            'month': day.month,
            'active_page': 'notebook_by_date',
            'active_menu': 'notebook',
            'due_time': '',
        })


class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'noteapp/edit_note.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Отримуємо адресу попередньої сторінки
        referer = self.request.META.get('HTTP_REFERER')
        if referer:
            context['return_url'] = referer
        context['due_time'] = self.object.due_time.strftime('%H:%M') if self.object.due_time else ''
        context['active_menu'] = 'notebook'
        context['active_page'] = 'note_edit'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Пробуємо витягнути return_url із POST
        return_url = self.request.POST.get('return_url')
        if return_url:
            return redirect(return_url)
        return response

    def get_success_url(self):
        # fallback якщо немає return_url
        return reverse('noteapp:notebook_by_date', kwargs={'date': self.object.doe_date})


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = 'noteapp/note_confirm_delete.html'

    def get_success_url(self):
        date_str = self.object.doe_date.isoformat()
        page = self.request.POST.get('page')
        url = reverse('noteapp:notebook_by_date', kwargs={'date': date_str})
        return f"{url}?page={page}" if page else url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'notebook'
        return context
