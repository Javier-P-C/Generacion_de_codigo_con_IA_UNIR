from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .permissions import IsManager
from .serializers import EmployeeSerializer

Employee = get_user_model()


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):  # type: ignore[override]
        # Allow read for authenticated users, write for managers only
        perms = super().get_permissions()
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [IsManager()]
        return perms
