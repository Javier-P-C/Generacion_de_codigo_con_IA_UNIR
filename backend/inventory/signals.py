from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from products.models import Product
from .models import Inventory


@receiver(post_save, sender=Product)
def create_inventory_for_product(sender, instance: Product, created: bool, **kwargs):  # noqa: D401
    """Create an inventory record for each new product."""
    if created:
        Inventory.objects.create(product=instance, quantity=0)
