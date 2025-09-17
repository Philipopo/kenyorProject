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

from .serializers import StorageBinSerializer, ItemSerializer, StockRecordSerializer, ExpiryTrackedItemSerializer, LocationEventSerializer
from accounts.permissions import APIKeyPermission
from .models import LocationEvent, Item, StockRecord, StorageBin  # Import models directly

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
    from accounts.models import PagePermission
    perm = PagePermission.objects.filter(page_name=page).first()
    if not perm:
        return 1
    return ROLE_LEVELS.get(perm.min_role, 1)

def get_action_required_level(action_name: str) -> int:
    from accounts.models import ActionPermission
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
        total_bin_locations = StorageBin.objects.count()
        total_active_rentals = StockRecord.objects.filter(quantity__gt=0).count()
        total_expired_items = Item.objects.filter(expiry_date__lte=date.today()).count()
        data = [
            {"id": 1, "title": "Total Items", "value": total_items, "change": "+0%", "trend": "neutral"},
            {"id": 2, "title": "Total Bin Locations", "value": total_bin_locations, "change": "+0%", "trend": "neutral"},
            {"id": 3, "title": "Total Active Rentals", "value": total_active_rentals, "change": "+0%", "trend": "neutral"},
            {"id": 4, "title": "Total Expired Items", "value": total_expired_items, "change": "+0%", "trend": "neutral"},
            {"id": 5, "title": "Total Stocks", "value": total_stocks, "change": "+0%", "trend": "neutral"},
        ]
        return Response(data)

class StorageBinViewSet(viewsets.ModelViewSet):
    serializer_class = StorageBinSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        check_permission(self.request.user, page="storage_bins")
        queryset = StorageBin.objects.all().order_by('-id')
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
        check_permission(request.user, page="expired_items")
        search = request.query_params.get('search', '').strip()
        queryset = Item.objects.filter(expiry_date__lte=date.today()).order_by('-created_at')
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
        queryset = Item.objects.all().order_by('-id')
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
        queryset = StockRecord.objects.select_related('item').order_by('-created_at')
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(item__name__icontains=search))
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        check_permission(self.request.user, action="create_stock_record")
        stock_record = serializer.save(user=self.request.user)

        if stock_record.storage_bin:
            stock_record.storage_bin.update_used()

    def perform_update(self, serializer):
        check_permission(self.request.user, action="update_stock_record")
        old_record = self.get_object()
        new_record = serializer.save(user=self.request.user)

        if new_record.storage_bin:
            new_record.storage_bin.update_used()

    def perform_destroy(self, instance):
        check_permission(self.request.user, action="delete_stock_record")
        if instance.storage_bin:
            instance.storage_bin.update_used()
        instance.delete()

class ExpiryTrackedItemViewSet(viewsets.ModelViewSet):
    serializer_class = ExpiryTrackedItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        from .models import ExpiryTrackedItem
        check_permission(self.request.user, page="expiry_tracked_items")
        queryset = ExpiryTrackedItem.objects.all().order_by('-id')
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(batch__icontains=search))
        return queryset

    def perform_create(self, serializer):
        from .models import ExpiryTrackedItem
        check_permission(self.request.user, action="create_expiry_tracked_item")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        from .models import ExpiryTrackedItem
        check_permission(self.request.user, action="update_expiry_tracked_item")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        check_permission(self.request.user, action="delete_expiry_tracked_item")
        instance.delete()

class IoTEventView(APIView):
    permission_classes = [APIKeyPermission]
    
    def process_iot_event(self, data):
        """Process IoT event data and return response data or error"""
        serializer = LocationEventSerializer(data=data)
        if not serializer.is_valid():
            logger.error(f"[IoTEventView] Invalid IoT event payload: {serializer.errors}")
            return None, serializer.errors
        
        storage_bin = serializer.validated_data['storage_bin']
        item = serializer.validated_data['item']
        event = serializer.validated_data['event']
        quantity = serializer.validated_data['quantity']
        timestamp = serializer.validated_data.get('timestamp', timezone.now())
        
        try:
            with transaction.atomic():
                # Create the LocationEvent
                event_obj = LocationEvent.objects.create(
                    storage_bin=storage_bin,
                    item=item,
                    event=event,
                    quantity=quantity,
                    timestamp=timestamp,
                    processed=True  # Mark as processed immediately
                )
                
                # Find or create StockRecord for this item and bin
                stock_record, created = StockRecord.objects.get_or_create(
                    item=item,
                    storage_bin=storage_bin,
                    defaults={
                        'quantity': 0,
                        'location': f"{storage_bin.row}-{storage_bin.rack}",
                        'user': None
                    }
                )
                
                # Update stock record based on event
                if event == 'item_added':
                    stock_record.quantity += quantity
                    item.quantity += quantity
                elif event == 'item_removed':
                    # Ensure we don't remove more than available
                    if stock_record.quantity < quantity:
                        quantity = stock_record.quantity  # Only remove what's available
                    stock_record.quantity -= quantity
                    item.quantity = max(0, item.quantity - quantity)
                
                # Save changes
                stock_record.save()
                item.save()
                
                # Refresh the storage_bin to get updated used value
                storage_bin.refresh_from_db()
                
                logger.info(f"[IoTEventView] IoT event processed: {event} at {storage_bin.bin_id} for {item.name}, quantity: {quantity}")
                
                return {
                    "message": "Event processed successfully",
                    "event_id": event_obj.id,
                    "location": f"{storage_bin.row}-{storage_bin.rack}",
                    "item": item.name,
                    "quantity": quantity,
                    "bin_used_capacity": storage_bin.used
                }, None
                
        except Exception as e:
            logger.error(f"[IoTEventView] Error processing IoT event: {str(e)}")
            return None, {"error": str(e)}

    def get(self, request):
        data = {
            'location': request.query_params.get('location'),
            'item_name': request.query_params.get('item_name'),
            'event': request.query_params.get('event'),
            'quantity': request.query_params.get('quantity'),
            'timestamp': request.query_params.get('timestamp')
        }
        
        response_data, error = self.process_iot_event(data)
        if error:
            return Response(error, status=400)
        return Response(response_data, status=200)

    def post(self, request):
        response_data, error = self.process_iot_event(request.data)
        if error:
            return Response(error, status=400)
        return Response(response_data, status=200)