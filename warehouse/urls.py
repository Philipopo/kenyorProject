from django.urls import path
from .views import WarehouseItemListCreateView

urlpatterns = [
    path('items/', WarehouseItemListCreateView.as_view(), name='warehouse-items'),
]
