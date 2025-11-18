from __future__ import annotations

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Sale, SaleDetail
from .serializers import (
    SaleCreateSerializer,
    SaleDetailSerializer,
    SaleSerializer,
)


class SaleViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Sale.objects.select_related('employee').all().order_by('-date')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):  # type: ignore[override]
        if self.action == 'create':
            return SaleCreateSerializer
        return SaleSerializer

    def create(self, request, *args, **kwargs):  # type: ignore[override]
        """Use write serializer for input and read serializer for output.

        This avoids trying to serialize non-model fields like `items` on the
        write serializer.
        """
        write_serializer = SaleCreateSerializer(data=request.data, context={'request': request})
        write_serializer.is_valid(raise_exception=True)
        sale = write_serializer.save()

        read_serializer = SaleSerializer(sale, context={'request': request})
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'], url_path='details')
    def details(self, request, pk=None):  # type: ignore[override]
        sale = self.get_object()
        details = SaleDetail.objects.filter(sale=sale).select_related('product')
        serializer = SaleDetailSerializer(details, many=True)
        return Response(serializer.data)
