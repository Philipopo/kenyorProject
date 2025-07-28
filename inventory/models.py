from django.db import models
from django.conf import settings

from accounts.models import User
from django.contrib.postgres.fields import JSONField  # For customFields

class StorageBin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bin_id = models.CharField(max_length=50, unique=True)
    row = models.CharField(max_length=20)        # ✅ New field
    rack = models.CharField(max_length=20)       # ✅ New field
    shelf = models.CharField(max_length=20)      # ✅ New field
    type = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    used = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.bin_id

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
    name = models.CharField(max_length=255)  # ✅ NEW
    quantity = models.PositiveIntegerField(default=0)  # ✅ NEW
    part_number = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    batch = models.CharField(max_length=255)
    custom_fields = models.JSONField()
    expiry_date = models.DateField()

    def __str__(self):
        return self.name or self.part_number

class StockRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    critical = models.BooleanField(default=False)

    def __str__(self):
        return self.item

