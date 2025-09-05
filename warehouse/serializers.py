# warehouse/serializers.py
from rest_framework import serializers
from .models import WarehouseItem
from product_documentation.models import ProductSerialNumber

class WarehouseItemSerializer(serializers.ModelSerializer):
    serial_number = serializers.SlugRelatedField(
        slug_field='serial_number',
        queryset=ProductSerialNumber.objects.all()
    )
    product_name = serializers.CharField(source='serial_number.inflow.product_name', read_only=True)
    sku = serializers.CharField(source='serial_number.inflow.sku', read_only=True)

    class Meta:
        model = WarehouseItem
        fields = ['id', 'serial_number', 'product_name', 'sku', 'location', 'status', 'last_updated']
        read_only_fields = ['last_updated', 'updated_by']

class ProductSerialNumberSerializer(serializers.ModelSerializer):
    inflow = serializers.SerializerMethodField()

    class Meta:
        model = ProductSerialNumber
        fields = ['id', 'serial_number', 'inflow', 'status']
        read_only_fields = ['status']

    def get_inflow(self, obj):
        return {'product_name': obj.inflow.product_name if obj.inflow else 'Unknown'}