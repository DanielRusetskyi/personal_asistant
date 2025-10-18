from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Thread, ThreadMember
from django.db.models import Count, Q

User = get_user_model()


def get_or_create_lobby(slug="general", title="General"):
    t, created = Thread.objects.get_or_create(
        type=Thread.TYPE_LOBBY,
        slug=slug,
        defaults={"title": title, "is_public": True},
    )

    return t


@transaction.atomic
def get_or_create_dm(user_a, user_b):
    if user_a.id == user_b.id:
        raise ValueError("Cannot start DM with yourself")

    a, b = sorted([user_a.id, user_b.id])

    # шукаємо тред, де є обидва учасники
    t = (Thread.objects
         .filter(type=Thread.TYPE_DM, members__user_id__in=[a, b])
         .annotate(mcount=Count("members", filter=Q(members__user_id__in=[a, b]), distinct=True))
         .filter(mcount=2)
         .first())

    if not t:
        t = Thread.objects.create(
            type=Thread.TYPE_DM,
            title=f"{user_a.username} ↔ {user_b.username}",
            is_public=False,
        )
        ThreadMember.objects.bulk_create([
            ThreadMember(thread=t, user_id=a),
            ThreadMember(thread=t, user_id=b),
        ])

    return t


@transaction.atomic
def create_group(owner, title, is_public=False):
    t = Thread.objects.create(type=Thread.TYPE_GROUP, title=title, is_public=is_public)
    ThreadMember.objects.create(thread=t, user=owner)
    return t


