from datetime import datetime
from django.utils import timezone
from rest_framework import serializers
from .models import StorageBin, Item, StockRecord, LocationEvent, ExpiryTrackedItem
import logging

logger = logging.getLogger(__name__)

class StorageBinSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageBin
        fields = ['id', 'bin_id', 'row', 'rack', 'shelf', 'type', 'capacity', 'used', 'description', 'user']
        read_only_fields = ['user', 'used']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'quantity', 'part_number', 'manufacturer', 'contact', 'batch', 'expiry_date', 'custom_fields', 'user', 'created_at']
        read_only_fields = ['user']

class StockRecordSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    storage_bin_id = serializers.CharField(source='storage_bin.bin_id', read_only=True, allow_null=True)
    item = ItemSerializer(read_only=True)  # Add nested ItemSerializer

    class Meta:
        model = StockRecord
        fields = ['id', 'item', 'item_name', 'storage_bin', 'storage_bin_id', 'location', 'quantity', 'critical', 'user', 'created_at']
        read_only_fields = ['user', 'item_name', 'storage_bin_id', 'created_at']

class LocationEventSerializer(serializers.ModelSerializer):
    location = serializers.CharField(write_only=True)
    item_name = serializers.CharField(write_only=True)
    quantity = serializers.IntegerField(min_value=1, required=True)
    timestamp = serializers.CharField(required=False)

    class Meta:
        model = LocationEvent
        fields = ['location', 'item_name', 'event', 'quantity', 'timestamp']
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
        if isinstance(value, StorageBin):
            logger.debug(f"[LocationEventSerializer] Received StorageBin: {value.bin_id}, returning as is")
            return value
        if not isinstance(value, str):
            raise serializers.ValidationError(f"Location must be a string, got {type(value)}")
        
        # Normalize the location format (A1-R02)
        value = value.replace('–', '-').replace('—', '-').strip().upper()
        logger.debug(f"[LocationEventSerializer] Normalized location: {value}")
        
        if '-' not in value:
            raise serializers.ValidationError(f"Location must contain a hyphen, got: {value}")
        
        try:
            # Parse the location format (A1-R02)
            parts = value.split('-', 1)
            if len(parts) != 2:
                raise serializers.ValidationError(f"Location must be in format 'Aisle-Rack' (e.g., 'A1-R02')")
                
            row, rack = parts
            row, rack = row.strip(), rack.strip()
            logger.debug(f"[LocationEventSerializer] Split location: row={row}, rack={rack}")
            
            # Find the storage bin by row and rack
            storage_bin = StorageBin.objects.get(row__iexact=row, rack__iexact=rack)
            logger.debug(f"[LocationEventSerializer] Found StorageBin: {storage_bin.bin_id}")
            return storage_bin
        except ValueError as e:
            raise serializers.ValidationError(f"Invalid format: Location must be 'Aisle-Rack' (e.g., 'A1-R02'), error: {str(e)}")
        except StorageBin.DoesNotExist:
            raise serializers.ValidationError(f"No StorageBin found for location: {value}")

    def validate_event(self, value):
        valid_events = [choice[0] for choice in LocationEvent.EVENT_CHOICES]
        logger.debug(f"[LocationEventSerializer] Validating event: {value}")
        normalized_event = value.lower().replace(' ', '_')
        if normalized_event not in valid_events:
            raise serializers.ValidationError(f"Event must be one of: {', '.join(valid_events)}")
        return normalized_event

    def validate_timestamp(self, value):
        logger.debug(f"[LocationEventSerializer] Validating timestamp: {value}")
        if not value:
            return timezone.now()
        try:
            # Handle the format "13/09/2025 17:33:23"
            parsed = datetime.strptime(value, '%d/%m/%Y %H:%M:%S')
            return timezone.make_aware(parsed)
        except ValueError:
            try:
                return serializers.DateTimeField().to_internal_value(value)
            except serializers.ValidationError:
                raise serializers.ValidationError(
                    "Timestamp must be in 'DD/MM/YYYY HH:MM:SS' or ISO 8601 format"
                )

    def validate(self, data):
        logger.debug(f"[LocationEventSerializer] Validating data: {data}")
        data['item'] = self.validate_item_name(data.get('item_name'))
        data['storage_bin'] = self.validate_location(data.get('location'))
        data['quantity'] = data.get('quantity', 1)
        return data

class ExpiryTrackedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpiryTrackedItem
        fields = ['id', 'name', 'batch', 'quantity', 'expiry_date', 'user']
        read_only_fields = ['user']