from django.urls import path
from . import views


app_name = 'noteapp'

urlpatterns = [
    path('', views.main, name='main'),
    path('calendar/', views.calendar_view, name='calendar_current'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar'),
    path('tasks/<date>/', views.DayTaskView.as_view(), name='day_tasks'),
    path('tasks/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_edit'),
    path('task/', views.tasks_by_period_view, name='task_by_period'),
    path('task/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    # path('task/')
]