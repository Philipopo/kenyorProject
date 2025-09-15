from django.contrib import admin
from .models import StorageBin, ExpiryTrackedItem, Item, StockRecord, LocationEvent

@admin.register(StorageBin)
class StorageBinAdmin(admin.ModelAdmin):
    list_display = ('bin_id', 'row', 'rack', 'shelf', 'type', 'capacity', 'used', 'description')
    list_filter = ('row', 'rack', 'type')
    search_fields = ('bin_id', 'row', 'rack', 'shelf', 'description')

@admin.register(ExpiryTrackedItem)
class ExpiryTrackedItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch', 'quantity', 'expiry_date')
    list_filter = ('name', 'batch')
    search_fields = ('name', 'batch')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'part_number', 'manufacturer', 'expiry_date', 'created_at')
    list_filter = ('name', 'manufacturer')
    search_fields = ('name', 'part_number', 'manufacturer')

@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = ('item', 'created_at', 'quantity', 'storage_bin', 'location', 'critical')  # Removed 'category', added 'created_at'
    list_filter = ('critical', 'storage_bin', 'location')
    search_fields = ('item__name', 'location')
    autocomplete_fields = ['item', 'storage_bin']

@admin.register(LocationEvent)
class LocationEventAdmin(admin.ModelAdmin):
    list_display = ('storage_bin', 'item', 'event', 'quantity', 'timestamp', 'processed', 'created_at')
    list_filter = ('event', 'processed')
    search_fields = ('storage_bin__bin_id', 'item__name')
    date_hierarchy = 'timestamp'