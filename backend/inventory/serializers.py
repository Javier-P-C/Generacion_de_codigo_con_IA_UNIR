from __future__ import annotations

from rest_framework import serializers

from products.serializers import ProductSerializer
from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'product', 'quantity']


class InventoryIncreaseSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)
