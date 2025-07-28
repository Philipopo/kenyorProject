from rest_framework import serializers
from .models import DwellTime, EOQReport
from .models import StockAnalytics

class DwellTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DwellTime
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class StockAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAnalytics
        fields = ['id', 'item', 'category', 'turnover_rate', 'obsolescence_risk']

class EOQReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EOQReport
        fields = '__all__'
