from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import FinanceCategory, FinanceTransaction
from .serializers import FinanceCategorySerializer, FinanceTransactionSerializer

class UserFinanceCategoryList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = FinanceCategory.objects.filter(created_by=request.user)
        serializer = FinanceCategorySerializer(categories, many=True)
        return Response(serializer.data)


class UserFinanceTransactionList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = FinanceTransaction.objects.filter(created_by=request.user)
        serializer = FinanceTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class FinanceOverview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = FinanceTransaction.objects.filter(created_by=request.user)
        total_expenditure = sum(t.amount for t in transactions)
        total_transactions = transactions.count()
        total_budget = 12000000  # static or fetched from another model in future

        return Response({
            "budget": total_budget,
            "expenditure": total_expenditure,
            "transactions": total_transactions
        })

