from django.shortcuts import render

from rest_framework import generics
from .models import Receipt, StockReceipt, SigningReceipt
from .serializers import ReceiptSerializer, StockReceiptSerializer, SigningReceiptSerializer

# Archive
class ReceiptListCreateView(generics.ListCreateAPIView):
    queryset = Receipt.objects.all().order_by('-date')
    serializer_class = ReceiptSerializer

# Create
class StockReceiptCreateView(generics.ListCreateAPIView):
    queryset = StockReceipt.objects.all().order_by('-date')
    serializer_class = StockReceiptSerializer

# Signing
class SigningReceiptListCreateView(generics.ListCreateAPIView):
    queryset = SigningReceipt.objects.all().order_by('-date')
    serializer_class = SigningReceiptSerializer

