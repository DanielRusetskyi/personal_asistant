from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Thread, ThreadMember, Message
from .services import get_or_create_lobby, get_or_create_dm, create_group
from django.db.models import Count, Q

User = get_user_model()


def _back_to_chat_list(request):
    # повертай у свій індекс чатів
    return redirect("chat:home")


@login_required
def chat_home(request):
    # три великі плитки → Lobby / 1:1 / Groups
    return render(request, "chat/home.html")


# --- Lobby ---
@login_required
def lobby_list(request):
    # показати публічні лобі (можна тримати «general» за замовчуванням)
    get_or_create_lobby("general", "General")
    lobbies = Thread.objects.filter(type=Thread.TYPE_LOBBY, is_archived=False).order_by("title")
    return render(request, "chat/lobby_list.html", {"lobbies": lobbies})


@login_required
def lobby_room(request, slug):
    thread = get_object_or_404(Thread, type=Thread.TYPE_LOBBY, slug=slug, is_archived=False)
    # для лобі не обов'язково додавати в members, але зручно
    ThreadMember.objects.get_or_create(thread=thread, user=request.user)
    messages = thread.messages.select_related("user").order_by("-created")[:200]
    messages = reversed(list(messages))
    return render(request, "chat/thread.html", {"thread": thread, "messages": messages})


# --- Direct (1:1) ---
# @login_required
# def dm_list(request):
#     threads = (Thread.objects
#                .filter(type=Thread.TYPE_DM, members__user=request.user)
#                .distinct())
#     return render(request, "chat/dm_list.html", {"threads": threads})

@login_required
def dm_list(request):
    q = (request.GET.get("q") or "").strip()
    users = User.objects.exclude(id=request.user.id)
    if q:
        users = users.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))
    users = users.order_by("username")[:100]  # просте обмеження
    return render(request, "chat/dm_list.html", {"users": users, "q": q})



@login_required
def dm_contacts(request):
    """Список юзерів для старту приватного діалогу."""
    users = User.objects.exclude(pk=request.user.pk).order_by("username")
    return render(request, "chat/dm_contacts.html", {"users": users})


@login_required
def start_dm(request, user_id):
    if request.user.id == user_id:
        raise Http404()
    try:
        other = User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        raise Http404()
    t = get_or_create_dm(request.user, other)
    return redirect("chat:dm_thread", thread_id=t.id)


@login_required
def dm_thread(request, thread_id):
    # допускаємо лише учасників
    thread = get_object_or_404(
        Thread, pk=thread_id, type=Thread.TYPE_DM, members__user=request.user,
        is_archived=False
    )
    messages = thread.messages.select_related("user").order_by("-created")[:200]
    messages = list(messages)[::-1]
    return render(request, "chat/thread.html", {"thread": thread, "messages": messages})


# --- Groups ---
@login_required
def group_list(request):
    threads = (Thread.objects
               .filter(type=Thread.TYPE_GROUP, members__user=request.user, is_archived=False)
               .distinct()
               .order_by("-created"))
    return render(request, "chat/group_list.html", {"threads": threads})


@login_required
def group_create(request):
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip() or "New group"
        is_public = bool(request.POST.get("is_public"))
        t = create_group(request.user, title, is_public)
        return redirect("chat:group_thread", thread_id=t.id)
    return render(request, "chat/group_create.html")


@login_required
def thread_page(request, thread_id):
    # спільний рендер для DM і груп
    thread = get_object_or_404(Thread, pk=thread_id,
                               members__user=request.user,
                               is_archived=False)
    messages = thread.messages.select_related("user").order_by("created")[:200]
    messages = reversed(list(messages))
    context = {"thread": thread, "messages": messages}
    return render(request, "chat/thread.html", context)


@login_required
def thread_list(request):
    threads = (
        Thread.objects.filter(members__user=request.user, is_archived=False)
        .distinct()
        .order_by("-created")
    )
    context = {"threads": threads}
    return render(request, "chat/threads.html", context)


@login_required
@require_POST
def thread_leave(request, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id, is_archived=False, members__user=request.user)
    # видаляємо лише участь користувача
    ThreadMember.objects.filter(thread=thread, user=request.user).delete()

    # (опційно) якщо це DM і в чаті більше нікого — видалити весь тред
    if thread.type == Thread.TYPE_DM and not thread.members.exists():
        thread.delete()
        return _back_to_chat_list(request)

    # (опційно) якщо це GROUP і нікого не лишилось — теж видалити
    if thread.type == Thread.TYPE_GROUP and not thread.members.exists():
        thread.delete()
        return _back_to_chat_list(request)

    return _back_to_chat_list(request)


@login_required
@require_POST
def thread_archive(request, thread_id):
    # дозвіл: або staff, або owner (якщо додаси поле owner)
    if not request.user.is_staff:
        return redirect("chat:thread", thread_id=thread_id)

    thread = get_object_or_404(Thread, pk=thread_id, is_archived=False)
    thread.is_archived = True
    thread.archived_at = timezone.now()
    thread.archived_by = request.user
    thread.save(update_fields=["is_archived", "archived_at", "archived_by"])
    return _back_to_chat_list(request)


@login_required
@require_POST
def thread_delete(request, thread_id):
    # дозвіл: або staff, або owner
    if not request.user.is_staff:
        return redirect("chat:thread", thread_id=thread_id)

    thread = get_object_or_404(Thread, pk=thread_id)
    thread.delete()
    return _back_to_chat_list(request)



