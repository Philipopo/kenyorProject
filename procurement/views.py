# procurement/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Requisition, PurchaseOrder, POItem, Receiving, GoodsReceipt, Vendor
from .serializers import (
    RequisitionSerializer,
    PurchaseOrderSerializer,
    POItemSerializer,
    ReceivingSerializer,
    GoodsReceiptSerializer,
    VendorSerializer,
)
from accounts.permissions import DynamicPermission

class RequisitionViewSet(viewsets.ModelViewSet):
    queryset = Requisition.objects.all()
    serializer_class = RequisitionSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'requisitions'
    required_permissions = {
        'create': 'create_requisition',
        'update': 'update_requisition',
        'partial_update': 'update_requisition',
        'destroy': 'delete_requisition',
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'vendors'
    required_permissions = {
        'create': 'add_vendor',
        'update': 'update_vendor',
        'partial_update': 'update_vendor',
        'destroy': 'delete_vendor',
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'purchase_orders'
    required_permissions = {
        'create': 'create_purchase_order',
        'update': 'update_purchase_order',
        'partial_update': 'update_purchase_order',
        'destroy': 'delete_purchase_order',
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class POItemViewSet(viewsets.ModelViewSet):
    queryset = POItem.objects.all()
    serializer_class = POItemSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'po_items'
    required_permissions = {
        'create': 'create_po_item',
        'update': 'update_po_item',
        'partial_update': 'update_po_item',
        'destroy': 'delete_po_item',
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class ReceivingViewSet(viewsets.ModelViewSet):
    queryset = Receiving.objects.all()
    serializer_class = ReceivingSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'receiving'
    required_permissions = {
        'create': 'create_receiving',
        'update': 'update_receiving',
        'partial_update': 'update_receiving',
        'destroy': 'delete_receiving',
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)


class GoodsReceiptViewSet(viewsets.ModelViewSet):
    queryset = GoodsReceipt.objects.all()
    serializer_class = GoodsReceiptSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'goods_receipts'
    required_permissions = {
        'create': 'create_goods_receipt',
        'update': 'update_goods_receipt',
        'partial_update': 'update_goods_receipt',
        'destroy': 'delete_goods_receipt',
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)