from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DeleteView
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

from .services import create_note_for_user
from .utils import get_day_context


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
        "active_page": "task"
    })


def main(request):
    return render(request, 'noteapp/index.html')


def calendar_view(request, year=None, month=None):
    today = timezone.localdate()
    if not year or not month:
        year = today.year
        month = today.month

    import calendar

    calendar.setfirstweekday(calendar.MONDAY)
    cal = calendar.Calendar()

    current_date = date(year, month, 1)

    month_days = cal.monthdatescalendar(year, month)
    if current_date < today.replace(day=1):
        messages.warning(request, "⚠️ Ви переглядаєте місяць, який вже минув.")

    context = {
        "calendar_weeks": month_days,
        "current_date": date(year, month, 1),
        "prev_month": (month - 1) if month > 1 else 12,
        "prev_year": year if month > 1 else year - 1,
        "next_month": (month + 1) if month < 12 else 1,
        "next_year": year if month < 12 else year + 1,
        "today": today,
        "active_page": 'calendar'
    }
    return render(request, "noteapp/calendar.html", context)


def task(request):

    return render(request, 'noteapp/task.html', {
        'active_page': 'task'
    })


# class DayTaskView(LoginRequiredMixin, View):
#     def get(self, request, date=timezone.localdate()):
#         # if not date:
#         #     day = timezone.localdate()
#         # else:
#         day = datetime.strptime(date, "%Y-%m-%d").date()
#         # day = datetime.strptime(date, "%Y-%m-%d").date()
#         prev_day = day - timedelta(days=1)
#         next_day = day + timedelta(days=1)
#         notes = Note.objects.filter(doe_date=day, user=request.user).order_by('due_time')
#
#         paginator = Paginator(notes_list, 7)  # нотаток на сторінку
#         page_number = request.GET.get('page')
#         notes = paginator.get_page(page_number)
#
#         return render(request, 'noteapp/day_tasks.html', {
#             'notes': notes,
#             'day': day.strftime('%Y-%m-%d'),
#             "prev_day": prev_day.strftime('%Y-%m-%d'),
#             "next_day": next_day.strftime('%Y-%m-%d'),
#             'active_page': 'calendar'
#         })
class DayTaskView(LoginRequiredMixin, View):
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
            'prev_day': (day - timedelta(days=1)).strftime('%Y-%m-%d'),
            'next_day': (day + timedelta(days=1)).strftime('%Y-%m-%d'),
        })

        return render(request, 'noteapp/day_tasks.html', context)


class CreateDayTaskView(LoginRequiredMixin, View):
    def get(self, request, date):
        context = get_day_context(request, date)
        context['form'] = NoteForm(initial={'doe_date': context['day']})
        context['active_page'] = 'calendar'
        return render(request, 'noteapp/create_day_tasks.html', context)
        # day = datetime.strptime(date, "%Y-%m-%d").date()
        # today = timezone.localdate()
        # if day < today:
        #     messages.warning(request, f"⚠️ Ви переглядаєте минулу дату: {day.strftime('%d.%m.%Y')}")
        #     form_disabled = True
        # else:
        #     form_disabled = False
        #
        # notes_list = Note.objects.filter(doe_date=day, user=request.user).order_by('due_time')
        #
        # paginator = Paginator(notes_list, 7)  # нотаток на сторінку
        # page_number = request.GET.get('page')
        # notes = paginator.get_page(page_number)
        #
        # form = NoteForm(initial={'doe_date': day})
        # return render(request, 'noteapp/create_day_tasks.html', {
        #     'notes': notes,
        #     'form': form,
        #     'day': day,
        #     'active_page': 'calendar',
        #     'form_disabled': form_disabled
        # })

    def post(self, request, date):
        form = NoteForm(request.POST)
        page = request.POST.get('page')
        if form.is_valid():
            note_data = form.cleaned_data
            note_data["doe_date"] = datetime.strptime(date, "%Y-%m-%d").date()
            create_note_for_user(request.user, note_data)
            # note = form.save(commit=False)
            # note.user = request.user
            # note.doe_date = datetime.strptime(date, "%Y-%m-%d").date()
            # note.save()
            # form.save_m2m()
            url = reverse('noteapp:create_day_tasks', kwargs={'date': date})
            if page:
                return redirect(f"{url}?page={page}")
            return redirect(url)
        day = datetime.strptime(date, "%Y-%m-%d").date()
        notes = Note.objects.filter(doe_date=day, user=request.user)
        return render(request, 'noteapp/create_day_tasks.html', {
            'notes': notes,
            'form': form,
            'day': day,
            'active_page': 'calendar',
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
        return reverse('noteapp:create_day_tasks', kwargs={'date': self.object.doe_date})


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = 'noteapp/note_confirm_delete.html'

    def get_success_url(self):
        date_str = self.object.doe_date.isoformat()
        page = self.request.POST.get('page')
        url = reverse('noteapp:create_day_tasks', kwargs={'date': date_str})
        return f"{url}?page={page}" if page else url
