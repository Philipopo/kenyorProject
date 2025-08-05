from datetime import date
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import StorageBin, Item, StockRecord
from .serializers import (
    StorageBinSerializer,
    ItemSerializer,
    StockRecordSerializer,
)

from accounts.models import PagePermission, ActionPermission   # ✅ new imports


# -----------------------------
# Role mapping
# -----------------------------
ROLE_LEVELS = {
    'staff': 1,
    'finance_manager': 2,
    'operational_manager': 3,
    'md': 4,
    'admin': 99,
}

def get_user_role_level(user):
    return ROLE_LEVELS.get(user.role, 0)


# -----------------------------
# Permission helpers
# -----------------------------
def get_page_required_level(page):
    perm = PagePermission.objects.filter(page_name=page).first()
    if not perm:
        return 1
    return ROLE_LEVELS.get(perm.min_role, 1)   


def get_action_required_level(action_name: str) -> int:
    """Fetch required role level for an action. Defaults to 1 (staff)."""
    try:
        perm = ActionPermission.objects.get(action_name=action_name)
        return ROLE_LEVELS.get(perm.minimum_role, 1)
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


# -----------------------------
# Views
# -----------------------------
class InventoryMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        check_permission(request.user, page="inventory_metrics")   # ✅ page permission check

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
        check_permission(self.request.user, page="storage_bins")   # ✅ page check
        return StorageBin.objects.all()

    def perform_create(self, serializer):
        check_permission(self.request.user, action="create_storage_bin")  # ✅ action check
        serializer.save(user=self.request.user)


class ExpiredItemListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        check_permission(request.user, page="expired_items")   # ✅ page check
        expired_items = Item.objects.filter(expiry_date__lte=date.today())
        serializer = ItemSerializer(expired_items, many=True)
        return Response(serializer.data)


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        check_permission(self.request.user, page="items")   # ✅ page check
        return Item.objects.all()

    def perform_create(self, serializer):
        check_permission(self.request.user, action="create_item")  # ✅ action check
        serializer.save(user=self.request.user)


class StockRecordViewSet(viewsets.ModelViewSet):
    serializer_class = StockRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        check_permission(self.request.user, page="stock_records")   # ✅ page check
        return StockRecord.objects.all()

    def perform_create(self, serializer):
        check_permission(self.request.user, action="create_stock_record")  # ✅ action check
        serializer.save(user=self.request.user)
