# analytics/urls.py
from django.urls import path
from .views import DashboardMetricsView, UserDwellTimeListView, UserEOQReportListView, UserStockAnalyticsListView

urlpatterns = [
    path('dashboard/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
    path('dwell/', UserDwellTimeListView.as_view(), name='dwell-time-list'),
    path('eoq/', UserEOQReportListView.as_view(), name='eoq-report-list'),
    path('stock/', UserStockAnalyticsListView.as_view(), name='stock-analytics'),
]