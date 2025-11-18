from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django.contrib.auth import get_user_model
from rest_framework import serializers

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .models import Employee as EmployeeType
else:  # runtime
    EmployeeType = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = EmployeeType
        fields = ['id', 'username', 'email', 'name', 'role', 'is_active', 'is_superuser', 'password']
        read_only_fields = ['id', 'is_superuser']

    def create(self, validated_data: dict[str, Any]) -> EmployeeType:
        password = validated_data.pop('password', None)
        user = EmployeeType(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance: EmployeeType, validated_data: dict[str, Any]) -> EmployeeType:
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
