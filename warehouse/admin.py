# warehouse/admin.py
from django.contrib import admin
from .models import WarehouseItem

class WarehouseItemAdmin(admin.ModelAdmin):
    list_display = ['get_serial_number', 'get_product_name', 'get_sku', 'location', 'status', 'last_updated']
    list_filter = ['status', 'location']
    search_fields = ['serial_number__serial_number', 'serial_number__inflow__product_name', 'serial_number__inflow__sku']

    def get_serial_number(self, obj):
        return obj.serial_number.serial_number
    get_serial_number.short_description = 'Serial Number'

    def get_product_name(self, obj):
        return obj.serial_number.inflow.product_name
    get_product_name.short_description = 'Product Name'

    def get_sku(self, obj):
        return obj.serial_number.inflow.sku
    get_sku.short_description = 'SKU'

admin.site.register(WarehouseItem, WarehouseItemAdmin)