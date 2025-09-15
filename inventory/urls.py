from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StorageBinViewSet,
    ItemViewSet,
    StockRecordViewSet,
    ExpiryTrackedItemViewSet,
    ExpiredItemListView,
    InventoryMetricsView,
    IoTEventView,
)

router = DefaultRouter()
router.register('bins', StorageBinViewSet, basename='bins')
router.register('items', ItemViewSet, basename='items')
router.register('stocks', StockRecordViewSet, basename='stocks')
router.register('expiry-tracked-items', ExpiryTrackedItemViewSet, basename='expiry-tracked-items')

urlpatterns = [
    path('', include(router.urls)),
    path('expiries/', ExpiredItemListView.as_view()),
    path('metrics/', InventoryMetricsView.as_view(), name='inventory-metrics'),
    path('iot-event/', IoTEventView.as_view(), name='iot-event'),
]