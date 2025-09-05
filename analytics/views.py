# analytics/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework import status
from accounts.permissions import DynamicPermission
from .models import DwellTime, EOQReport, StockAnalytics
from .serializers import DwellTimeSerializer, EOQReportSerializer, StockAnalyticsSerializer

class DashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'analytics_dashboard'  # New page permission

    def get(self, request):
        user = request.user
        # Metric Counts (requires Alert, AuditLog, Rental models)
        total_stock_items = StockAnalytics.objects.filter(user=user).count()
        low_stock_items = StockAnalytics.objects.filter(user=user, category='C').count()  # Fixed 'classification' to 'category'
        # Skip undefined models for now
        dwell_items = DwellTime.objects.filter(user=user).count()
        eoq_reports = EOQReport.objects.filter(user=user).count()
        receipt_count = Receipt.objects.filter(user=user).count()

        metrics = [
            {"id": 1, "title": "Total Stock Items", "value": total_stock_items, "trend": "up", "change": "+12%"},
            {"id": 2, "title": "Low Stock Items", "value": low_stock_items, "trend": "down", "change": "-4%"},
            {"id": 4, "title": "Dwell Records", "value": dwell_items, "trend": "neutral", "change": "0%"},
            {"id": 5, "title": "EOQ Reports", "value": eoq_reports, "trend": "up", "change": "+5%"},
            {"id": 6, "title": "Receipts Logged", "value": receipt_count, "trend": "up", "change": "+3%"},
        ]

        # Skip activities due to undefined AuditLog
        return Response({"metrics": metrics, "activities": []})

class UserDwellTimeListView(ListAPIView):
    serializer_class = DwellTimeSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'analytics_dwell'

    def get_queryset(self):
        return DwellTime.objects.filter(user=self.request.user)

    def post(self, request):
        serializer = DwellTimeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserEOQReportListView(ListAPIView):
    serializer_class = EOQReportSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'analytics_eoq'

    def get_queryset(self):
        return EOQReport.objects.filter(user=self.request.user)

    def post(self, request):
        serializer = EOQReportSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserStockAnalyticsListView(APIView):
    permission_classes = [IsAuthenticated, DynamicPermission]
    page_permission_name = 'analytics_stock'

    def get(self, request):
        data = StockAnalytics.objects.filter(user=request.user)
        serializer = StockAnalyticsSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StockAnalyticsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)