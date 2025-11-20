from __future__ import annotations

from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'presentation', 'substance', 'price']

    def validate_price(self, value):
        """Validate that price is positive."""
        if value < 0:
            raise serializers.ValidationError("Price must be a positive value.")
        return value
