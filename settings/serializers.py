from rest_framework import serializers
from .models import BrandAsset, ERPIntegration, Tracker

class BrandAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandAsset
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'upload_date']


class ERPIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPIntegration
        fields = '__all__'
        read_only_fields = ['synced_by', 'last_sync']


class TrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracker
        fields = '__all__'
        read_only_fields = ['created_by', 'last_ping']
