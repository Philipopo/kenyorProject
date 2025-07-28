from django.urls import path
from .views import UserDwellTimeListView, UserEOQReportListView, UserStockAnalyticsListView
from .views import EOQReportListView

urlpatterns = [
    path('dwell/', UserDwellTimeListView.as_view(), name='dwell-time-list'),
    path('eoq/', UserEOQReportListView.as_view(), name='eoq-report-list'),
    path('stock/', UserStockAnalyticsListView.as_view(), name='stock-analytics'),
    path('eoq/', EOQReportListView.as_view(), name='eoq-list'),
]
