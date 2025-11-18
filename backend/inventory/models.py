from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models

from products.models import Product


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gte=0), name='quantity_non_negative'),
        ]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.product.name} - {self.quantity}"
