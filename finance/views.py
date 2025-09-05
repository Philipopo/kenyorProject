# finance/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import FinanceCategory, FinanceTransaction
from .serializers import FinanceCategorySerializer, FinanceTransactionSerializer
from accounts.permissions import DynamicPermission

class FinanceCategoryViewSet(ModelViewSet):
    queryset = FinanceCategory.objects.all()
    serializer_class = FinanceCategorySerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'finance_categories'
    required_permissions = {
        'create': 'create_finance_category',
        'update': 'update_finance_category',
        'partial_update': 'update_finance_category',
        'destroy': 'delete_finance_category',
    }

    def get_queryset(self):
        return FinanceCategory.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)

class FinanceTransactionViewSet(ModelViewSet):
    queryset = FinanceTransaction.objects.all()
    serializer_class = FinanceTransactionSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'finance_transactions'
    required_permissions = {
        'create': 'create_finance_transaction',
        'update': 'update_finance_transaction',
        'partial_update': 'update_finance_transaction',
        'destroy': 'delete_finance_transaction',
    }

    def get_queryset(self):
        return FinanceTransaction.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)

class FinanceOverview(APIView):
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'finance_overview'

    def get(self, request):
        transactions = FinanceTransaction.objects.filter(created_by=request.user)
        total_expenditure = sum(t.amount for t in transactions)
        total_transactions = transactions.count()
        total_budget = 12000000  # Static or fetched from another model in future

        return Response({
            "budget": total_budget,
            "expenditure": total_expenditure,
            "transactions": total_transactions
        })