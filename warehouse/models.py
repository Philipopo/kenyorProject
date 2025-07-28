from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WarehouseItem(models.Model):
    item = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('In Stock', 'In Stock'),
        ('Low', 'Low'),
        ('Empty', 'Empty'),
    ])
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.item
