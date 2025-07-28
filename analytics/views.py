from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from .models import DwellTime, EOQReport
from .models import StockAnalytics
from .serializers import StockAnalyticsSerializer
from .serializers import DwellTimeSerializer, EOQReportSerializer
from .serializers import EOQReportSerializer
from receipts.models import Receipt  # optional

from django.utils.timezone import now
from datetime import timedelta


class DashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # ===== Metric Counts =====
        total_stock_items = StockAnalytics.objects.filter(user=user).count()
        low_stock_items = StockAnalytics.objects.filter(user=user, classification='C').count()
        active_alerts = Alert.objects.filter(user=user, resolved=False).count()
        dwell_items = DwellTime.objects.filter(user=user).count()
        eoq_reports = EOQReport.objects.filter(user=user).count()
        receipt_count = Receipt.objects.filter(user=user).count()
        active_rentals = Rental.objects.filter(user=user, status='active').count()

        # ===== Dashboard Metrics Array =====
        metrics = [
            {
                "id": 1,
                "title": "Total Stock Items",
                "value": total_stock_items,
                "trend": "up",
                "change": "+12%"
            },
            {
                "id": 2,
                "title": "Low Stock Items",
                "value": low_stock_items,
                "trend": "down",
                "change": "-4%"
            },
            {
                "id": 3,
                "title": "Active Alerts",
                "value": active_alerts,
                "trend": "up",
                "change": "+9%"
            },
            {
                "id": 4,
                "title": "Dwell Records",
                "value": dwell_items,
                "trend": "neutral",
                "change": "0%"
            },
            {
                "id": 5,
                "title": "EOQ Reports",
                "value": eoq_reports,
                "trend": "up",
                "change": "+5%"
            },
            {
                "id": 6,
                "title": "Receipts Logged",
                "value": receipt_count,
                "trend": "up",
                "change": "+3%"
            },
            {
                "id": 7,
                "title": "Active Rentals",
                "value": active_rentals,
                "trend": "down",
                "change": "-1%"
            },
        ]

        # ===== Recent Audit Activities =====
        recent_logs = AuditLog.objects.filter(user=user).order_by("-timestamp")[:5]
        activities = [
            {
                "id": log.id,
                "action": log.action,
                "item": log.entity,
                "time": log.timestamp.strftime("%d %b, %I:%M %p"),
            }
            for log in recent_logs
        ]

        return Response({
            "metrics": metrics,
            "activities": activities
        })



class UserDwellTimeListView(ListAPIView):
    serializer_class = DwellTimeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DwellTime.objects.filter(user=self.request.user)


class UserEOQReportListView(ListAPIView):
    serializer_class = EOQReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EOQReport.objects.filter(user=self.request.user)


class UserStockAnalyticsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = StockAnalytics.objects.filter(user=request.user)
        serializer = StockAnalyticsSerializer(data, many=True)
        return Response(serializer.data)

class EOQReportListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        eoq_reports = EOQReport.objects.filter(user=request.user)
        serializer = EOQReportSerializer(eoq_reports, many=True)
        return Response(serializer.data)

