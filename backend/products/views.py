from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from employees.permissions import IsManager
from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):  # type: ignore[override]
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [IsManager()]
        return super().get_permissions()
