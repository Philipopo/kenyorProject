from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RequisitionViewSet,
    PurchaseOrderViewSet,
    POItemViewSet,
    ReceivingViewSet,
    GoodsReceiptCreateAPIView,
    VendorViewSet
)

router = DefaultRouter()
router.register('requisitions', RequisitionViewSet)
router.register('purchase-orders', PurchaseOrderViewSet)
router.register('po-items', POItemViewSet)
router.register('receivings', ReceivingViewSet, basename='receiving')
router.register(r'vendors', VendorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('grn/', GoodsReceiptCreateAPIView.as_view(), name='grn-create'),
]
