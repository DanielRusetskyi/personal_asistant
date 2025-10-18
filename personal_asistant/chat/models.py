from django.utils import timezone

from django.db import models
from django.conf import settings


class Thread(models.Model):
    TYPE_LOBBY = "lobby"
    TYPE_DM = "dm"
    TYPE_GROUP = "group"
    TYPE_CHOICES = [
        (TYPE_LOBBY, "Lobby"),
        (TYPE_DM, "Direct"),
        (TYPE_GROUP, "Group"),
    ]
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_threads",
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_LOBBY)
    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True, max_length=64, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="archived_threads"
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title or f'{self.type}#{self.pk}'


class ThreadMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, related_name='members', on_delete=models.CASCADE)
    joined = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'thread')


class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=4000)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('created',)




