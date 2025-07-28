from django.contrib import admin
from .models import StorageBin, ExpiryTrackedItem, Item, StockRecord

@admin.register(StorageBin)
class StorageBinAdmin(admin.ModelAdmin):
    list_display = ['bin_id', 'type', 'capacity', 'used', 'user']

@admin.register(ExpiryTrackedItem)
class ExpiryTrackedItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'batch', 'quantity', 'expiry_date', 'user']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['part_number', 'manufacturer', 'batch', 'user']

@admin.register(StockRecord)
class StockRecordAdmin(admin.ModelAdmin):
    list_display = ['item', 'category', 'location', 'quantity', 'critical', 'user']

