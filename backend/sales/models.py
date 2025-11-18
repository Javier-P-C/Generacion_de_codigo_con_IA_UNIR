from __future__ import annotations

from django.db import models

from employees.models import Employee
from products.models import Product


class Sale(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='sales')
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Sale #{self.id} - {self.total}"


class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Sale #{self.sale.id} - {self.product.name} x{self.quantity}"
