from django.db import models
from django.conf import settings
from django.db.models import JSONField  # Changed import

class StorageBin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bin_id = models.CharField(max_length=50, unique=True)
    row = models.CharField(max_length=20, db_index=True)
    rack = models.CharField(max_length=20, db_index=True)
    shelf = models.CharField(max_length=20)
    type = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    used = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('row', 'rack')
        indexes = [
            models.Index(fields=['row', 'rack']),
        ]

    def __str__(self):
        return f"{self.bin_id} ({self.row}-{self.rack})"

class ExpiryTrackedItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    batch = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.batch})"

class Item(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    part_number = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    batch = models.CharField(max_length=255)
    custom_fields = JSONField()  # Updated to django.db.models.JSONField
    expiry_date = models.DateField()

    def __str__(self):
        return self.name or self.part_number

class StockRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # Allow null for IoT
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='stock_records')
    storage_bin = models.ForeignKey(StorageBin, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField()
    critical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} at {self.storage_bin or self.location} ({self.quantity})"

class LocationEvent(models.Model):
    EVENT_CHOICES = [
        ('item_added', 'Item Added'),
        ('item_removed', 'Item Removed'),
    ]
    storage_bin = models.ForeignKey(StorageBin, on_delete=models.CASCADE, related_name='events')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='events')
    event = models.CharField(max_length=20, choices=EVENT_CHOICES)
    timestamp = models.DateTimeField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.storage_bin.bin_id} - {self.item.name} - {self.event} at {self.timestamp}"