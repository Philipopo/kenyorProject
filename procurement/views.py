from django.shortcuts import render
from rest_framework import generics, permissions

from rest_framework import viewsets
from .models import Requisition, PurchaseOrder, POItem, Receiving, GoodsReceipt, Vendor
from .serializers import RequisitionSerializer, PurchaseOrderSerializer, POItemSerializer, ReceivingSerializer, GoodsReceiptSerializer, VendorSerializer
from rest_framework.permissions import IsAuthenticated

class RequisitionViewSet(viewsets.ModelViewSet):
    queryset = Requisition.objects.all()
    serializer_class = RequisitionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]

class POItemViewSet(viewsets.ModelViewSet):
    queryset = POItem.objects.all()
    serializer_class = POItemSerializer
    permission_classes = [IsAuthenticated]

class ReceivingViewSet(viewsets.ModelViewSet):
    queryset = Receiving.objects.all()
    serializer_class = ReceivingSerializer
    permission_classes = [IsAuthenticated]


class GoodsReceiptCreateAPIView(generics.CreateAPIView):
    queryset = GoodsReceipt.objects.all()
    serializer_class = GoodsReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

