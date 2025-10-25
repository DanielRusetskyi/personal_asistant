from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST

from .forms import GroupCreateForm, GroupMembersForm
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
@transaction.atomic
def group_create(request):
    if request.method == "POST":
        f1 = GroupCreateForm(request.POST)
        f2 = GroupMembersForm(request.POST, user=request.user)
        if f1.is_valid() and f2.is_valid():
            t = Thread.objects.create(
                type=Thread.TYPE_GROUP,
                title=f1.cleaned_data["title"].strip(),
                owner=request.user,
                is_public=False,
            )
            # обов'язково додати власника
            ThreadMember.objects.create(thread=t, user=request.user)
            # додати обраних
            sel = list(f2.cleaned_data["members"])
            ThreadMember.objects.bulk_create(
                [ThreadMember(thread=t, user=u) for u in sel],
                ignore_conflicts=True
            )
            return redirect("chat:group_thread", thread_id=t.id)
    else:
        f1 = GroupCreateForm()
        f2 = GroupMembersForm(user=request.user)

    return render(request, "chat/group_create.html", {"form": f1, "form_members": f2})


@login_required
@transaction.atomic
def group_manage(request, group_id):
    """Керування складом (доступ тільки власнику)."""
    thread = get_object_or_404(Thread, pk=group_id, type=Thread.TYPE_GROUP, archived_at__isnull=True)
    if thread.owner_id != request.user.id:
        return HttpResponseForbidden("Only owner can manage members")

    # поточні учасники (крім власника)
    current_ids = set(thread.members.exclude(user=thread.owner).values_list("user_id", flat=True))

    if request.method == "POST":
        form = GroupMembersForm(request.POST, user=request.user)
        if form.is_valid():
            new_ids = set(form.cleaned_data["members"].values_list("id", flat=True))
            # додати
            to_add = new_ids - current_ids
            ThreadMember.objects.bulk_create(
                [ThreadMember(thread=thread, user_id=uid) for uid in to_add],
                ignore_conflicts=True
            )
            # прибрати
            to_del = current_ids - new_ids
            if to_del:
                ThreadMember.objects.filter(thread=thread, user_id__in=to_del).delete()
            return redirect("chat:group_thread", thread_id=thread.id)
    else:
        # initial
        form = GroupMembersForm(
            user=request.user,
            initial={"members": list(current_ids)}
        )

    members_qs = thread.members.select_related("user")
    return render(request, "chat/group_manage.html", {
        "thread": thread,
        "form": form,
        "members": members_qs,
    })


@login_required
@transaction.atomic
def group_leave(request, group_id):
    thread = get_object_or_404(Thread, pk=group_id, type=Thread.TYPE_GROUP, archived_at__isnull=True)
    # власник не може просто "вийти", хай спершу передасть права або видалить
    if thread.owner_id == request.user.id:
        return HttpResponseForbidden("Owner cannot leave. Transfer ownership or delete the group.")
    ThreadMember.objects.filter(thread=thread, user=request.user).delete()
    return redirect("chat:home")


@login_required
@transaction.atomic
def group_delete(request, group_id):
    """Видалення (архівація) групи. Лише власник."""
    thread = get_object_or_404(Thread, pk=group_id, type=Thread.TYPE_GROUP, archived_at__isnull=True)
    if thread.owner_id != request.user.id:
        return HttpResponseForbidden("Only owner can delete the group")
    thread.archived_at = timezone.now()
    thread.archived_by = request.user
    thread.is_archived = True
    thread.save(update_fields=["archived_at", "archived_by", "is_archived"])
    return redirect("chat:home")


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



