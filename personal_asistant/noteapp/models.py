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
    description = models.CharField(max_length=150, verbose_name="Опис")
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
