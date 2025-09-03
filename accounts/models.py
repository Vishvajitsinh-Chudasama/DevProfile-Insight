from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('personal', 'Personal'),
        ('company', 'Company'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)  # ensure unique emails
    company_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username
