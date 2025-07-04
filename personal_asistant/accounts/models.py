from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Avatar')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone')

    class Meta:
        db_table = 'user'
    
    
    def __str__(self):
        return self.username
    


# Create your models here.

