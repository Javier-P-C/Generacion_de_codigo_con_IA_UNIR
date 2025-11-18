from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from employees.permissions import IsManager
from .models import Inventory
from .serializers import InventoryIncreaseSerializer, InventorySerializer


class InventoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Inventory.objects.select_related('product').all().order_by('id')
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='increase', permission_classes=[IsManager])
    def increase(self, request, pk=None):  # type: ignore[override]
        inventory = get_object_or_404(Inventory, pk=pk)
        serializer = InventoryIncreaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        inventory.quantity += amount
        inventory.save(update_fields=['quantity'])
        return Response(InventorySerializer(inventory).data)
