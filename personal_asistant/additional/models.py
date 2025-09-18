from django.db import models
from django.utils.text import slugify


class Station(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    stream_url = models.URLField(help_text="Прямий URL аудіо‑потоку (mp3/aac/ogg)")
    website_url = models.URLField(blank=True)
    icon_url = models.URLField(blank=True, help_text="Посилання на favicon/лого")
    country = models.CharField(max_length=60, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Через кому: news, jazz …")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "name")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name
