# inventory/views.py
from datetime import date
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import StorageBin, Item, StockRecord, ExpiryTrackedItem
from .serializers import (
    StorageBinSerializer,
    ItemSerializer,
    StockRecordSerializer,
    ExpiryTrackedItemSerializer,
)
from accounts.models import PagePermission, ActionPermission

ROLE_LEVELS = {
    'staff': 1,
    'finance_manager': 2,
    'operations_manager': 3,  # Fixed typo: operational_manager -> operations_manager
    'md': 4,
    'admin': 99,
}

def get_user_role_level(user):
    return ROLE_LEVELS.get(user.role, 0)

def get_page_required_level(page):
    perm = PagePermission.objects.filter(page_name=page).first()
    if not perm:
        return 1
    return ROLE_LEVELS.get(perm.min_role, 1)

def get_action_required_level(action_name: str) -> int:
    """Fetch required role level for an action. Defaults to 1 (staff)."""
    try:
        perm = ActionPermission.objects.get(action_name=action_name)
        return ROLE_LEVELS.get(perm.min_role, 1)
    except ActionPermission.DoesNotExist:
        return 1  # default to staff

def check_permission(user, page=None, action=None):
    """Raise error if user doesn’t meet required role level."""
    user_level = get_user_role_level(user)

    if page:
        required = get_page_required_level(page)
        if user_level < required:
            raise PermissionDenied(f"Access denied: {page} requires role level {required}")

    if action:
        required = get_action_required_level(action)
        if user_level < required:
            raise PermissionDenied(f"Access denied: {action} requires role level {required}")

class InventoryMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        check_permission(request.user, page="inventory_metrics")
        total_items = Item.objects.count()
        total_stocks = StockRecord.objects.count()
        data = [
            {"id": 1, "title": "Total Items", "value": total_items, "change": "+0%", "trend": "neutral"},
            {"id": 2, "title": "Total Stocks", "value": total_stocks, "change": "+0%", "trend": "neutral"},
        ]
        return Response(data)

class StorageBinViewSet(viewsets.ModelViewSet):
    serializer_class = StorageBinSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        check_permission(self.request.user, page="storage_bins")
        return StorageBin.objects.all()

    def perform_create(self, serializer):
        check_permission(self.request.user, action="create_storage_bin")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        check_permission(self.request.user, action="update_storage_bin")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        check_permission(self.request.user, action="delete_storage_bin")
        instance.delete()

class ExpiredItemListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        check_permission(self.request.user, page="expired_items")
        expired_items = Item.objects.filter(expiry_date__lte=date.today())
        serializer = ItemSerializer(expired_items, many=True)
        return Response(serializer.data)

class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        check_permission(self.request.user, page="items")
        return Item.objects.all()

    def perform_create(self, serializer):
        check_permission(self.request.user, action="create_item")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        check_permission(self.request.user, action="update_item")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        check_permission(self.request.user, action="delete_item")
        instance.delete()

class StockRecordViewSet(viewsets.ModelViewSet):
    serializer_class = StockRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        check_permission(self.request.user, page="stock_records")
        queryset = StockRecord.objects.all()
        print("StockRecord queryset:", list(queryset.values()))  # Debug log
        return queryset

    def perform_create(self, serializer):
        print("Creating stock with data:", serializer.validated_data)
        print("User:", self.request.user)  # Debug log
        check_permission(self.request.user, action="create_stock_record")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        check_permission(self.request.user, action="update_stock_record")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        check_permission(self.request.user, action="delete_stock_record")
        instance.delete()

class ExpiryTrackedItemViewSet(viewsets.ModelViewSet):
    serializer_class = ExpiryTrackedItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        check_permission(self.request.user, page="expiry_tracked_items")
        return ExpiryTrackedItem.objects.all()

    def perform_create(self, serializer):
        check_permission(self.request.user, action="create_expiry_tracked_item")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        check_permission(self.request.user, action="update_expiry_tracked_item")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        check_permission(self.request.user, action="delete_expiry_tracked_item")
        instance.delete()