from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        RESIDENT = 'RESIDENT', 'Resident'
        SECURITY = 'SECURITY', 'Security'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.RESIDENT
    )

    def __str__(self):
        return f"{self.username} - {self.role}"
