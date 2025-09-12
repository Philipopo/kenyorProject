# product_documentation/admin.py
from django.contrib import admin
from .models import ProductInflow, ProductSerialNumber, ProductOutflow

class ProductSerialNumberInline(admin.TabularInline):
    model = ProductSerialNumber
    extra = 1  # Number of empty forms to display
    fields = ['serial_number', 'status', 'created_at']
    readonly_fields = ['created_at']
    can_delete = True

class ProductInflowAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'sku', 'production_date', 'quantity', 'cost', 'created_by', 'created_at']
    list_filter = ['production_date', 'created_by']
    search_fields = ['product_name', 'sku']
    inlines = [ProductSerialNumberInline]
    readonly_fields = ['created_at', 'created_by']
    date_hierarchy = 'production_date'

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class ProductOutflowAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'customer_name', 'sales_order', 'dispatch_date', 'quantity', 'responsible_staff', 'created_at']
    list_filter = ['dispatch_date', 'responsible_staff']
    search_fields = ['customer_name', 'sales_order', 'product__product_name', 'product__sku']
    readonly_fields = ['created_at', 'responsible_staff']
    date_hierarchy = 'dispatch_date'

    def product_name(self, obj):
        return obj.product.product_name
    product_name.short_description = 'Product Name'

    def save_model(self, request, obj, form, change):
        if not change:  # Only set responsible_staff on creation
            obj.responsible_staff = request.user
        super().save_model(request, obj, form, change)

class ProductSerialNumberAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'inflow', 'status', 'created_at']
    list_filter = ['status', 'inflow']
    search_fields = ['serial_number', 'inflow__product_name', 'inflow__sku']
    readonly_fields = ['created_at']

admin.site.register(ProductInflow, ProductInflowAdmin)
admin.site.register(ProductSerialNumber, ProductSerialNumberAdmin)
admin.site.register(ProductOutflow, ProductOutflowAdmin)