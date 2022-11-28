from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom user model
class User(AbstractUser):
    """
    Custom user model with email and pass as authentication
    """

    phone = models.CharField(max_length=10, blank=True, unique=True)
    wa_sending = models.BooleanField(default=False)

    def __str__(self):
        return self.get_full_name()