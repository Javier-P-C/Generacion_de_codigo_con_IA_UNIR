from __future__ import annotations

from django.db import models


class Product(models.Model):
    class Presentations(models.TextChoices):
        TABLETS = 'tablets', 'Tablets'
        CAPSULES = 'capsules', 'Capsules'
        SYRUPS = 'syrups', 'Syrups'
        SUSPENSIONS = 'suspensions', 'Suspensions'
        SOLUTIONS = 'solutions', 'Solutions'
        PILLS = 'pills', 'Pills'
        INJECTABLES = 'injectables', 'Injectables'

    name = models.CharField(max_length=150)
    presentation = models.CharField(max_length=20, choices=Presentations.choices)
    substance = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name} ({self.presentation})"
