from django.db import models
from django.conf import settings

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    condition = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='equipment')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Rental(models.Model):
    code = models.CharField(max_length=100, unique=True, blank=True)
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rentals')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='rentals')
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Overdue', 'Overdue')])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_rentals')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Check if the instance is being created
        if is_new and not self.code:
            super().save(*args, **kwargs)  # Save first to get an ID
            self.code = f"RENT-{self.id:06d}"
            super().save(update_fields=['code'])  # Update only the code field
        else:
            super().save(*args, **kwargs)  # Normal save for updates

    def __str__(self):
        return f"{self.code} - {self.renter.full_name} - {self.equipment.name}"

        

class RentalPayment(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Pending', 'Pending')])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='rental_payments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rental.code} - ₦{self.amount_paid} ({self.status})"