from django.urls import path
from . import views


app_name = 'noteapp'

urlpatterns = [
    path('', views.notebook, name='notebook'),
    path('calendar/', views.calendar_view, name='calendar_current'),
    path('calendar/<str:date_>/', views.calendar_view, name='calendar_by_date'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar'),
    path('notebook/<str:date>/', views.DayTaskView.as_view(), name='notebook_by_date'),
    path('task/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_edit'),
    path('task/', views.tasks_by_period_view, name='task_by_period'),
    path('tasks/<date>/', views.DayTaskView_.as_view(), name='day_tasks'),
    path('task/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    path('toggle-task-status/', views.toggle_task_status, name='toggle_task_status')
    # path('task/')
]