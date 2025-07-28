from rest_framework import serializers
from .models import WarehouseItem

class WarehouseItemSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.email', read_only=True)

    class Meta:
        model = WarehouseItem
        fields = ['id', 'item', 'location', 'status', 'last_updated', 'updated_by', 'updated_by_name']
        read_only_fields = ['updated_by', 'last_updated']
