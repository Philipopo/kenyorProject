# receipts/urls.py
from django.urls import path
from .views import ReceiptListCreateView, StockReceiptCreateView, SigningReceiptListCreateView

urlpatterns = [
    path('', ReceiptListCreateView.as_view(), name='receipt-list-create'),
    path('stock/', StockReceiptCreateView.as_view(), name='stock-receipt-create'),
    path('signing/', SigningReceiptListCreateView.as_view(), name='signing-receipt-list-create'),
]