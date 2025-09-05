# warehouse/models.py
from django.db import models
from django.conf import settings
from product_documentation.models import ProductSerialNumber

class WarehouseItem(models.Model):
    serial_number = models.ForeignKey(ProductSerialNumber, on_delete=models.CASCADE, related_name='warehouse_items')
    location = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=(('in_stock', 'In Stock'), ('reserved', 'Reserved'), ('dispatched', 'Dispatched')),
        default='in_stock'
    )
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-last_updated']

    def __str__(self):
        return f"{self.serial_number.serial_number} at {self.location}"