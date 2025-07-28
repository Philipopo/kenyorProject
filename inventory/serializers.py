from rest_framework import serializers
from .models import StorageBin, ExpiryTrackedItem, Item, StockRecord

class StorageBinSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageBin
        fields = '__all__'
        read_only_fields = ['user']

class ExpiryTrackedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiryTrackedItem
        fields = '__all__'
        read_only_fields = ['user']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        exclude = []
        read_only_fields = ['user']


class StockRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockRecord
        fields = '__all__'
        read_only_fields = ['user']
