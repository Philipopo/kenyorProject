from rest_framework import serializers
from .models import StorageBin, Item, StockRecord, LocationEvent, ExpiryTrackedItem
import logging

logger = logging.getLogger(__name__)

class StorageBinSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageBin
        fields = ['id', 'bin_id', 'row', 'rack', 'shelf', 'type', 'capacity', 'used', 'description', 'user']
        read_only_fields = ['user']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'quantity', 'part_number', 'manufacturer', 'contact', 'batch', 'expiry_date', 'custom_fields', 'user']
        read_only_fields = ['user']

class StockRecordSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    storage_bin_id = serializers.CharField(source='storage_bin.bin_id', read_only=True, allow_null=True)

    class Meta:
        model = StockRecord
        fields = ['id', 'item', 'item_name', 'storage_bin', 'storage_bin_id', 'category', 'location', 'quantity', 'critical', 'user', 'created_at']
        read_only_fields = ['user', 'item_name', 'storage_bin_id', 'created_at']

class LocationEventSerializer(serializers.ModelSerializer):
    location = serializers.CharField(write_only=True)
    item_name = serializers.CharField(write_only=True)

    class Meta:
        model = LocationEvent
        fields = ['location', 'item_name', 'event', 'timestamp']
        extra_kwargs = {
            'timestamp': {'required': False},
        }

    def validate_item_name(self, value):
        logger.debug(f"[LocationEventSerializer] Validating item_name: {value}")
        try:
            item = Item.objects.get(name__iexact=value)
            logger.debug(f"[LocationEventSerializer] Found Item: {item.name}")
            return item
        except Item.DoesNotExist:
            raise serializers.ValidationError(f"No Item found with name: {value}")

    def validate_location(self, value):
        logger.debug(f"[LocationEventSerializer] Validating location: value={value}, type={type(value)}")
        # Handle case where value is already a StorageBin
        if isinstance(value, StorageBin):
            logger.debug(f"[LocationEventSerializer] Received StorageBin: {value.bin_id}, returning as is")
            return value
        if not isinstance(value, str):
            raise serializers.ValidationError(f"Location must be a string, got {type(value)}")
        # Normalize hyphens and whitespace
        value = value.replace('–', '-').replace('—', '-').strip()
        logger.debug(f"[LocationEventSerializer] Normalized location: {value}")
        if '-' not in value:
            raise serializers.ValidationError(f"Location must contain a hyphen, got: {value}")
        try:
            row, rack = value.split('-', 1)
            row, rack = row.strip(), rack.strip()
            logger.debug(f"[LocationEventSerializer] Split location: row={row}, rack={rack}")
            storage_bin = StorageBin.objects.get(row__iexact=row, rack__iexact=rack)
            logger.debug(f"[LocationEventSerializer] Found StorageBin: {storage_bin.bin_id}")
            return storage_bin
        except ValueError as e:
            raise serializers.ValidationError(f"Invalid format: Location must be 'Aisle-Rack' (e.g., 'A1-R02'), error: {str(e)}")
        except StorageBin.DoesNotExist:
            raise serializers.ValidationError(f"No StorageBin found for row={row}, rack={rack}")

    def validate_event(self, value):
        valid_events = [choice[0] for choice in LocationEvent.EVENT_CHOICES]
        logger.debug(f"[LocationEventSerializer] Validating event: {value}")
        if value not in valid_events:
            raise serializers.ValidationError(f"Event must be one of: {', '.join(valid_events)}")
        return value

    def validate(self, data):
        logger.debug(f"[LocationEventSerializer] Validating data: {data}")
        data['item'] = self.validate_item_name(data.get('item_name'))
        # Ensure validate_location receives the raw location string
        data['storage_bin'] = self.validate_location(data.get('location'))
        return data

class ExpiryTrackedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiryTrackedItem
        fields = ['id', 'name', 'batch', 'quantity', 'expiry_date', 'user']
        read_only_fields = ['user']