from datetime import date
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.utils import timezone
import logging

from .models import StorageBin, Item, StockRecord, ExpiryTrackedItem, LocationEvent
from .serializers import (
    StorageBinSerializer,
    ItemSerializer,
    StockRecordSerializer,
    ExpiryTrackedItemSerializer,
    LocationEventSerializer,
)
from accounts.models import PagePermission, ActionPermission
from accounts.permissions import APIKeyPermission  # Add import

logger = logging.getLogger(__name__)

ROLE_LEVELS = {
    'staff': 1,
    'finance_manager': 2,
    'operations_manager': 3,
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
    try:
        perm = ActionPermission.objects.get(action_name=action_name)
        return ROLE_LEVELS.get(perm.min_role, 1)
    except ActionPermission.DoesNotExist:
        return 1

def check_permission(user, page=None, action=None):
    user_level = get_user_role_level(user)
    if page:
        required = get_page_required_level(page)
        if user_level < required:
            raise PermissionDenied(f"Access denied: {page} requires role level {required}")
    if action:
        required = get_action_required_level(action)
        if user_level < required:
            raise PermissionDenied(f"Access denied: {action} requires role level {required}")

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class InventoryMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        check_permission(request.user, page="inventory_metrics")
        search = request.query_params.get('search', '').strip()
        total_items = Item.objects.filter(Q(name__icontains=search) | Q(part_number__icontains=search)).count() if search else Item.objects.count()
        total_stocks = StockRecord.objects.filter(Q(item__name__icontains=search)).count() if search else StockRecord.objects.count()
        data = [
            {"id": 1, "title": "Total Items", "value": total_items, "change": "+0%", "trend": "neutral"},
            {"id": 2, "title": "Total Stocks", "value": total_stocks, "change": "+0%", "trend": "neutral"},
        ]
        return Response(data)

class StorageBinViewSet(viewsets.ModelViewSet):
    serializer_class = StorageBinSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        check_permission(self.request.user, page="storage_bins")
        queryset = StorageBin.objects.all()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(bin_id__icontains=search) | Q(description__icontains=search))
        return queryset

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
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        check_permission(self.request.user, page="expired_items")
        search = request.query_params.get('search', '').strip()
        queryset = Item.objects.filter(expiry_date__lte=date.today())
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(part_number__icontains=search))
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ItemSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        check_permission(self.request.user, page="items")
        queryset = Item.objects.all()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(part_number__icontains=search))
        return queryset

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
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        check_permission(self.request.user, page="stock_records")
        queryset = StockRecord.objects.all()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(item__icontains=search))
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
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        check_permission(self.request.user, page="expiry_tracked_items")
        queryset = ExpiryTrackedItem.objects.all()
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(batch__icontains=search))
        return queryset

    def perform_create(self, serializer):
        check_permission(self.request.user, action="create_expiry_tracked_item")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        check_permission(self.request.user, action="update_expiry_tracked_item")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        check_permission(self.request.user, action="delete_expiry_tracked_item")
        instance.delete()




class IoTEventView(APIView):
    permission_classes = [APIKeyPermission]  # Use API key auth

    def get(self, request):
        # Extract query parameters
        data = {
            'location': request.query_params.get('location'),
            'item_name': request.query_params.get('item_name'),
            'event': request.query_params.get('event'),
            'timestamp': request.query_params.get('timestamp')
        }
        serializer = LocationEventSerializer(data=data)
        if not serializer.is_valid():
            logger.error(f"Invalid IoT event payload for GET: {serializer.errors}")
            return Response(serializer.errors, status=400)

        storage_bin = serializer.validated_data['storage_bin']
        item = serializer.validated_data['item']
        event = serializer.validated_data['event']
        timestamp = serializer.validated_data.get('timestamp', timezone.now())

        try:
            with transaction.atomic():
                # Log the event
                event_obj = LocationEvent.objects.create(
                    storage_bin=storage_bin,
                    item=item,
                    event=event,
                    timestamp=timestamp,
                    processed=True
                )

                # Update Item.quantity and create StockRecord
                if event == 'item_added':
                    item.quantity += 1
                    item.save()
                    StockRecord.objects.create(
                        item=item,
                        storage_bin=storage_bin,
                        category=item.manufacturer or 'General',
                        location=f"{storage_bin.row}-{storage_bin.rack}",
                        quantity=1,
                        critical=False,
                        user=None  # IoT events don't have a user
                    )
                    storage_bin.used += 1
                    storage_bin.save()
                elif event == 'item_removed':
                    if item.quantity <= 0:
                        logger.warning(f"Cannot remove item {item.name} from {storage_bin.bin_id}: quantity is {item.quantity}")
                        return Response({"error": f"Cannot remove item: {item.name} has quantity {item.quantity}"}, status=400)
                    item.quantity -= 1
                    item.save()
                    StockRecord.objects.create(
                        item=item,
                        storage_bin=storage_bin,
                        category=item.manufacturer or 'General',
                        location=f"{storage_bin.row}-{storage_bin.rack}",
                        quantity=-1,
                        critical=(item.quantity <= 0),
                        user=None
                    )
                    storage_bin.used = max(0, storage_bin.used - 1)
                    storage_bin.save()

            logger.info(f"IoT event processed via GET: {event} at {storage_bin.bin_id} for {item.name}")
            return Response({
                "message": "Event processed successfully",
                "event_id": event_obj.id,
                "location": f"{storage_bin.row}-{storage_bin.rack}",
                "item": item.name
            }, status=200)
        except Exception as e:
            logger.error(f"Error processing IoT event via GET: {str(e)}")
            return Response({"error": str(e)}, status=500)

    def post(self, request):
        serializer = LocationEventSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Invalid IoT event payload: {serializer.errors}")
            return Response(serializer.errors, status=400)

        storage_bin = serializer.validated_data['storage_bin']
        item = serializer.validated_data['item']
        event = serializer.validated_data['event']
        timestamp = serializer.validated_data.get('timestamp', timezone.now())

        try:
            with transaction.atomic():
                # Log the event
                event_obj = LocationEvent.objects.create(
                    storage_bin=storage_bin,
                    item=item,
                    event=event,
                    timestamp=timestamp,
                    processed=True
                )

                # Update Item.quantity and create StockRecord
                if event == 'item_added':
                    item.quantity += 1
                    item.save()
                    StockRecord.objects.create(
                        item=item,
                        storage_bin=storage_bin,
                        category=item.manufacturer or 'General',
                        location=f"{storage_bin.row}-{storage_bin.rack}",
                        quantity=1,
                        critical=False,
                        user=None  # IoT events don't have a user
                    )
                    storage_bin.used += 1
                    storage_bin.save()
                elif event == 'item_removed':
                    if item.quantity <= 0:
                        logger.warning(f"Cannot remove item {item.name} from {storage_bin.bin_id}: quantity is {item.quantity}")
                        return Response({"error": f"Cannot remove item: {item.name} has quantity {item.quantity}"}, status=400)
                    item.quantity -= 1
                    item.save()
                    StockRecord.objects.create(
                        item=item,
                        storage_bin=storage_bin,
                        category=item.manufacturer or 'General',
                        location=f"{storage_bin.row}-{storage_bin.rack}",
                        quantity=-1,
                        critical=(item.quantity <= 0),
                        user=None
                    )
                    storage_bin.used = max(0, storage_bin.used - 1)
                    storage_bin.save()

            logger.info(f"IoT event processed: {event} at {storage_bin.bin_id} for {item.name}")
            return Response({
                "message": "Event processed successfully",
                "event_id": event_obj.id,
                "location": f"{storage_bin.row}-{storage_bin.rack}",
                "item": item.name
            }, status=200)
        except Exception as e:
            logger.error(f"Error processing IoT event: {str(e)}")
            return Response({"error": str(e)}, status=500)