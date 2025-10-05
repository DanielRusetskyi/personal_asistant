from django.urls import path
from . import views, views_push, views_settings
from django.http import HttpResponse
from django.conf import settings


app_name = 'noteapp'


urlpatterns = [
    path('', views.notebook, name='notebook'),
    path('calendar/', views.calendar_view, name='calendar_current'),
    path('calendar/<str:date_>/', views.calendar_view, name='calendar_by_date'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar'),
    path('notebook/<str:date>/', views.DayTaskView.as_view(), name='notebook_by_date'),
    path("notebook/<str:date>/create/", views.CreateTaskView.as_view(), name="notebook_by_date_create"),
    path('task/', views.tasks_by_period_view, name='task_by_period'),
    path('tasks/<date>/', views.DayTaskView.as_view(), name='day_tasks'),
    path('task/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    path('task/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_edit'),
    path('toggle-task-status/', views.toggle_task_status, name='toggle_task_status'),
    path("push/subscribe/", views_push.push_subscribe, name="push_subscribe"),
    path("push/unsubscribe/", views_push.push_unsubscribe, name="push_unsubscribe"),
    # path("push/vapid-public.txt", views_push.vapid_public, name="vapid_public"),
    path("push/public-key/", views_push.vapid_public, name="push_public_key"),
    # path("settings/", views_settings.SettingsView.as_view(), name="settings"),
    path("push/toggle/", views_push.push_toggle, name="push_toggle"),
    path("push/status/", views_push.push_status,    name="push_status"),
    # path("settings/push/", views_settings.SettingsPushViews.as_view(), name="settings_push"),
    # path("settings/appearance/", views_settings.SettingsAppearanceViews.as_view(), name="settings_appearance"),
]
