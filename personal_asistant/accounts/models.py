from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary import uploader
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.URLField(max_length=500, blank=True, null=True, verbose_name="Avatar")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone')

    class Meta:
        db_table = 'user'

    def upload_image(self, file):
        """
        Завантажує зображення користувача на Cloudinary з постійним public_id.
        При кожному завантаженні файл буде перезаписано.
        """
        if not file:
            return

        try:
            result = uploader.upload(
                file,
                public_id=f"avatars/user_{self.id}",
                overwrite=True,
                folder=None,
                use_filename=True,
                unique_filename=False,
                resource_type="image"
            )
            self.avatar = result.get("secure_url")
            self.save(update_fields=["avatar"])
        except Exception as e:
            logger.error(f"Не вдалося завантажити аватар для користувача {self.username}: {e}")

    def __str__(self):
        return self.username


class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    push_enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UserSettings(user={self.user.name}, push_enabled={self.push_enabled})"
