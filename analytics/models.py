from django.db import models
from django.conf import settings
from accounts.models import User  # adjust if your User model is elsewhere

class DwellTime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField()
    is_aging = models.BooleanField(default=False)
    storage_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class EOQReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    part_number = models.CharField(max_length=50)
    demand_rate = models.PositiveIntegerField(help_text="Units/year")
    order_cost = models.DecimalField(max_digits=10, decimal_places=2)
    holding_cost = models.DecimalField(max_digits=10, decimal_places=2)
    eoq = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class StockAnalytics(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stock_analytics')
    item = models.CharField(max_length=255)
    category = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')])
    turnover_rate = models.DecimalField(max_digits=10, decimal_places=2)
    obsolescence_risk = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item} - {self.category}"
