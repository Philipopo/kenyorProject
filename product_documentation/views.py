# product_documentation/views.py
from rest_framework import viewsets, permissions
from .models import ProductInflow, ProductOutflow
from .serializers import ProductInflowSerializer, ProductOutflowSerializer
from accounts.permissions import HasMinimumRole

class ProductInflowViewSet(viewsets.ModelViewSet):
    queryset = ProductInflow.objects.all()
    serializer_class = ProductInflowSerializer
    permission_classes = [permissions.IsAuthenticated, HasMinimumRole]
    required_role_level = 2  # finance_manager or higher

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)

class ProductOutflowViewSet(viewsets.ModelViewSet):
    queryset = ProductOutflow.objects.all()
    serializer_class = ProductOutflowSerializer
    permission_classes = [permissions.IsAuthenticated, HasMinimumRole]
    required_role_level = 2  # finance_manager or higher

    def perform_create(self, serializer):
        serializer.save(responsible_staff=self.request.user)

    def perform_update(self, serializer):
        serializer.save(responsible_staff=self.request.user)