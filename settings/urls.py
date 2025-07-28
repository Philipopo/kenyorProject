from django.urls import path
from . import views

urlpatterns = [
    path('branding/', views.BrandAssetListCreateView.as_view(), name='branding'),
    path('erp/', views.ERPIntegrationListCreateView.as_view(), name='erp'),
    path('tracker/', views.TrackerListCreateView.as_view(), name='tracker'),
]
