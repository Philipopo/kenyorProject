# finance/models.py
from django.db import models
from django.conf import settings

class FinanceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='finance_categories')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class FinanceTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('Purchase', 'Purchase'),
        ('Expense', 'Expense'),
    )

    ref = models.CharField(max_length=50, blank=True)  # No unique=True
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='finance_transactions')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to generate ID
        if not self.ref:
            self.ref = f"TRX-{self.id}"
            super().save(update_fields=['ref'])  # Update only ref
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.ref