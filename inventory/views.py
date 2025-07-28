from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import StorageBin, Item, StockRecord
from .serializers import (
    StorageBinSerializer,
    ItemSerializer,
    StockRecordSerializer,
)
from datetime import date
from rest_framework.exceptions import PermissionDenied
from accounts.permissions import HasMinimumRole

# Role mapping
ROLE_LEVELS = {
    'staff': 1,
    'finance_manager': 2,
    'operational_manager': 3,
    'md': 4,
    'admin': 99
}

def get_user_role_level(user):
    return ROLE_LEVELS.get(user.role, 0)

def can_view_all(user):
    return user.is_superuser or get_user_role_level(user) >= 0


class InventoryMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if can_view_all(user):
            total_items = Item.objects.count()
            total_stocks = StockRecord.objects.count()
        else:
            total_items = Item.objects.filter(user=user).count()
            total_stocks = StockRecord.objects.filter(user=user).count()

        data = [
            {
                "id": 1,
                "title": "Total Items",
                "value": total_items,
                "change": "+0%",
                "trend": "neutral"
            },
            {
                "id": 2,
                "title": "Total Stocks",
                "value": total_stocks,
                "change": "+0%",
                "trend": "neutral"
            }
        ]

        return Response(data)


class StorageBinViewSet(viewsets.ModelViewSet):
    serializer_class = StorageBinSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if can_view_all(user):
            return StorageBin.objects.all()
        return StorageBin.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpiredItemListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if can_view_all(user):
            expired_items = Item.objects.filter(expiry_date__lte=date.today())
        else:
            expired_items = Item.objects.filter(user=user, expiry_date__lte=date.today())
        serializer = ItemSerializer(expired_items, many=True)
        return Response(serializer.data)


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, HasMinimumRole]
    required_role_level = 3  # operational_manager, md, admin

    def get_queryset(self):
        user = self.request.user
        if can_view_all(user):
            return Item.objects.all()
        return Item.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




        
class StockRecordViewSet(viewsets.ModelViewSet):
    serializer_class = StockRecordSerializer
    permission_classes = [permissions.IsAuthenticated, HasMinimumRole]
    required_role_level = 3  # operational_manager, md, admin

    def get_queryset(self):
        user = self.request.user
        if can_view_all(user):
            return StockRecord.objects.all()
        return StockRecord.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
