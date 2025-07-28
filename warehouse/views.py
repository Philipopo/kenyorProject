from django.shortcuts import render
from rest_framework import generics, permissions
from .models import WarehouseItem
from .serializers import WarehouseItemSerializer

class WarehouseItemListCreateView(generics.ListCreateAPIView):
    serializer_class = WarehouseItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WarehouseItem.objects.filter(updated_by=self.request.user).order_by('-last_updated')

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)
