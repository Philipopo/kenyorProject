from django.contrib import admin
from .models import WarehouseItem

@admin.register(WarehouseItem)
class WarehouseItemAdmin(admin.ModelAdmin):
    list_display = ['item', 'location', 'status', 'last_updated', 'updated_by']
    search_fields = ['item', 'location', 'updated_by__email']

