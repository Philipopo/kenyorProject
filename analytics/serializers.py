# analytics/serializers.py
from rest_framework import serializers
from .models import DwellTime, EOQReport, StockAnalytics

class DwellTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DwellTime
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class EOQReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EOQReport
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class StockAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAnalytics
        fields = ['id', 'item', 'category', 'turnover_rate', 'obsolescence_risk']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)