from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class Employee(AbstractUser):
    class Roles(models.TextChoices):
        MANAGER = 'MANAGER', 'Manager'
        ASSISTANT = 'ASSISTANT', 'Assistant'

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.ASSISTANT)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.username} ({self.get_role_display()})"
