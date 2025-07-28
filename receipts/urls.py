from django.urls import path
from .views import ReceiptListCreateView, StockReceiptCreateView, SigningReceiptListCreateView

urlpatterns = [
    path('archive/', ReceiptListCreateView.as_view(), name='receipt-archive'),
    path('create/', StockReceiptCreateView.as_view(), name='stock-receipt-create'),
    path('signing/', SigningReceiptListCreateView.as_view(), name='signing-receipt'),
]
