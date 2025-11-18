from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from rest_framework import serializers

from inventory.models import Inventory
from products.serializers import ProductSerializer
from .models import Sale, SaleDetail


class SaleDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = SaleDetail
        fields = ['id', 'product', 'quantity', 'subtotal']


class SaleDetailCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class SaleSerializer(serializers.ModelSerializer):
    details = SaleDetailSerializer(many=True, read_only=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'employee', 'employee_name', 'date', 'total', 'details']
        read_only_fields = ['employee', 'date', 'total']


class SaleCreateSerializer(serializers.Serializer):
    items = SaleDetailCreateSerializer(many=True)

    def validate_items(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not items:
            raise serializers.ValidationError("At least one item is required.")
        return items

    def create(self, validated_data: dict[str, Any]) -> Sale:
        items = validated_data['items']
        employee = self.context['request'].user

        with transaction.atomic():
            sale = Sale.objects.create(employee=employee, total=Decimal('0.00'))
            total = Decimal('0.00')

            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']

                try:
                    inventory = Inventory.objects.select_for_update().get(product_id=product_id)
                except Inventory.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Inventory not found for product ID {product_id}."
                    )

                if inventory.quantity < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for product {inventory.product.name}. "
                        f"Available: {inventory.quantity}, Requested: {quantity}"
                    )

                inventory.quantity -= quantity
                inventory.save(update_fields=['quantity'])

                subtotal = inventory.product.price * Decimal(str(quantity))
                total += subtotal

                SaleDetail.objects.create(
                    sale=sale,
                    product=inventory.product,
                    quantity=quantity,
                    subtotal=subtotal,
                )

            sale.total = total
            sale.save(update_fields=['total'])

        return sale
