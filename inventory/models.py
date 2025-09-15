from django.db import models
from django.conf import settings
from django.db.models import JSONField, Sum

class StorageBin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bin_id = models.CharField(max_length=50, unique=True)
    row = models.CharField(max_length=20, db_index=True)
    rack = models.CharField(max_length=20, db_index=True)
    shelf = models.CharField(max_length=20)
    type = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    used = models.PositiveIntegerField(default=0)  # Updated via stock records
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('row', 'rack')
        indexes = [
            models.Index(fields=['row', 'rack']),
        ]

    def __str__(self):
        return f"{self.bin_id} ({self.row}-{self.rack})"

    def update_used(self):
        """Update the 'used' field by summing quantities from related StockRecord entries."""
        total_used = self.stock_records.aggregate(total=Sum('quantity'))['total'] or 0
        if total_used != self.used:
            self.used = total_used
            self.save(update_fields=['used'])

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
    custom_fields = JSONField()
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or self.part_number

class StockRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='stock_records')
    storage_bin = models.ForeignKey(StorageBin, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_records')
    location = models.CharField(max_length=100, blank=True)  # For IoT events without bin assignment
    quantity = models.IntegerField()
    critical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} at {self.storage_bin or self.location} ({self.quantity})"

    def save(self, *args, **kwargs):
        """Override save to update the related StorageBin's 'used' field."""
        super().save(*args, **kwargs)
        if self.storage_bin:
            self.storage_bin.update_used()

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
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.storage_bin.bin_id} - {self.item.name} - {self.event} at {self.timestamp}"

    def save(self, *args, **kwargs):
        """Override save to process the event and update StockRecord/StorageBin."""
        super().save(*args, **kwargs)
        if not self.processed:
            try:
                stock_record, created = StockRecord.objects.get_or_create(
                    item=self.item,
                    storage_bin=self.storage_bin,
                    defaults={'quantity': 0, 'user': self.storage_bin.user if self.storage_bin else None}
                )
                if self.event == 'item_added':
                    stock_record.quantity += self.quantity
                elif self.event == 'item_removed' and stock_record.quantity >= self.quantity:
                    stock_record.quantity -= self.quantity
                if stock_record.quantity < 0:
                    stock_record.quantity = 0
                stock_record.save()
                self.processed = True
                self.save(update_fields=['processed'])
            except Exception as e:
                print(f"Error processing event: {e}")