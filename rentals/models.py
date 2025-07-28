from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    condition = models.CharField(max_length=50)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Rental(models.Model):
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Overdue', 'Overdue')])

    def __str__(self):
        return f"{self.renter} - {self.equipment}"

class RentalPayment(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Pending', 'Pending')])

    def __str__(self):
        return f"{self.rental.renter} - {self.amount_paid} ({self.status})"

