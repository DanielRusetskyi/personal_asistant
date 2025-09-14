from django.db import models

from django.conf import settings


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=25, null=False,unique=True)

    def __str__(self):
        return f"{self.name}"


class Note(models.Model):
    PRIORITY_CHOICES = [
        ('high', '🔴 Високий'),
        ('medium', '🟡 Середній'),
        ('low', '⚪ Низький'),
    ]

    name = models.CharField(blank=True, null=True, max_length=50, verbose_name="Назва")
    description = models.CharField(max_length=250, verbose_name="Опис")
    done = models.BooleanField(default=False, verbose_name="Виконано")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    doe_date = models.DateField(null=True, blank=True, verbose_name="Дата виконання")
    due_time = models.TimeField(null=True, blank=True, verbose_name="Час виконання")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Пріоритет"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', verbose_name="Теги")

    def __str__(self):
        return f"{self.name} ({self.get_priority_display()})"  # type: ignore


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
