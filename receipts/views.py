# receipts/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Receipt, StockReceipt, SigningReceipt
from .serializers import ReceiptSerializer, StockReceiptSerializer, SigningReceiptSerializer
from accounts.permissions import DynamicPermission
# Removed incorrect imports: from .models import FinanceCategory, FinanceTransaction
# If needed, add: from finance.models import FinanceCategory, FinanceTransaction

class ReceiptListCreateView(APIView):
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'receipt_archive'
    # POST checks 'create_receipt' via DynamicPermission

    def get(self, request):
        receipts = Receipt.objects.all()  # Adjust filtering if needed
        serializer = ReceiptSerializer(receipts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReceiptSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Adjust to include created_by if added to model
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StockReceiptCreateView(APIView):
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'stock_receipts'
    # POST checks 'create_stock_receipt' via DynamicPermission

    def post(self, request):
        serializer = StockReceiptSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Adjust to include created_by if added to model
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SigningReceiptListCreateView(APIView):
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'signing_receipts'
    # POST checks 'create_signing_receipt' via DynamicPermission

    def get(self, request):
        receipts = SigningReceipt.objects.all()  # Adjust filtering if needed
        serializer = SigningReceiptSerializer(receipts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SigningReceiptSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Adjust to include created_by if added to model
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)