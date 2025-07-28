from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BrandAsset(models.Model):
    ASSET_TYPES = [
        ('Logo', 'Logo'),
        ('Letterhead', 'Letterhead'),
        ('Color Palette', 'Color Palette'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=ASSET_TYPES)
    file = models.FileField(upload_to='brand_assets/', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class ERPIntegration(models.Model):
    STATUS_CHOICES = [
        ('Connected', 'Connected'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
    ]
    system = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    last_sync = models.DateField(auto_now_add=True)
    synced_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.system


class Tracker(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
    ]
    device_id = models.CharField(max_length=50)
    asset = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    last_ping = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.device_id
