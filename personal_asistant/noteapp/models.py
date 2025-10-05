from django.db import models

from django.conf import settings
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=25, null=False, unique=True)

    def __str__(self):
        return f"{self.name}"


class Note(models.Model):
    class Priority(models.TextChoices):
        HIGH = "high",   _("🔴 High")
        MEDIUM = "medium", _("🟡 Medium")
        LOW = "low",    _("⚪ Low")

    name = models.CharField(blank=True, null=True, max_length=50, verbose_name=_("Name"))
    description = models.CharField(max_length=250, verbose_name=_("Description"))
    done = models.BooleanField(default=False, verbose_name=_("Done"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    doe_date = models.DateField(null=True, blank=True, verbose_name=_("Due date"))
    due_time = models.TimeField(null=True, blank=True, verbose_name=_("Due time"))
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name=_("Priority")
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"))
    tags = models.ManyToManyField('Tag', blank=True, verbose_name=_("Tags"))

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")
        ordering = ["-created"]

    def __str__(self):
        base = self.name or _("Without name")
        return f"{base} ({self.get_priority_display()})"


class PushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    endpoint = models.TextField()
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    ua = models.TextField(blank=True, default="", max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, default="")

    class Meta:
        unique_together = (("user", "endpoint"),)
        indexes = [
            models.Index(fields=["user"]),
        ]
