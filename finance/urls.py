from django.urls import path
from .views import UserFinanceCategoryList, UserFinanceTransactionList, FinanceOverview

urlpatterns = [
    path('categories/', UserFinanceCategoryList.as_view(), name='finance-categories'),
    path('transactions/', UserFinanceTransactionList.as_view(), name='finance-transactions'),
    path('overview/', FinanceOverview.as_view(), name='finance-overview'),
]
