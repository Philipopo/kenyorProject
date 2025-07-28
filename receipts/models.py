from django.db import models

class Receipt(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    issued_by = models.CharField(max_length=100)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.reference

class StockReceipt(models.Model):
    item = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    location = models.CharField(max_length=100)
    date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.item

class SigningReceipt(models.Model):
    recipient = models.CharField(max_length=100)
    signed_by = models.CharField(max_length=100)
    date = models.DateField()
    status = models.CharField(max_length=50, choices=[('Signed', 'Signed'), ('Pending', 'Pending')])

    def __str__(self):
        return f'{self.recipient} - {self.status}'

