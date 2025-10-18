from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_home, name="home"),

    path("lobby/", views.lobby_list, name="lobby_list"),
    path("lobby/<slug:slug>/", views.lobby_room, name="lobby_room"),

    path("dm/", views.dm_list, name="dm_list"),
    path("dm/", views.dm_contacts, name="dm_contacts"),
    path("dm/start/<int:user_id>/", views.start_dm, name="dm_start"),
    path("dm/<int:thread_id>/", views.thread_page, name="dm_thread"),

    path("groups/", views.group_list, name="group_list"),
    path("groups/create/", views.group_create, name="group_create"),
    path("groups/<int:thread_id>/", views.thread_page, name="group_thread"),

    path("threads/<int:thread_id>/leave/",   views.thread_leave,   name="leave"),
    path("threads/<int:thread_id>/archive/", views.thread_archive, name="archive"),
    path("threads/<int:thread_id>/delete/",  views.thread_delete,  name="delete"),
]
