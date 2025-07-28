from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Requisition(models.Model):
    item = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    department = models.CharField(max_length=100)
    purpose = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requisitions')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item} ({self.department})"


class Vendor(models.Model):
    STAR_CHOICES = [(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]

    name = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    lead_time = models.PositiveIntegerField(help_text="Lead time in days")
    ratings = models.IntegerField(choices=STAR_CHOICES, default=3)
    document = models.FileField(upload_to='vendor_documents/', blank=True, null=True)

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    requisition = models.ForeignKey('Requisition', on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey('Vendor', on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=255)
    eoq = models.PositiveIntegerField(default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"PO#{self.id} - {self.vendor.name if self.vendor else 'No Vendor'}"


class POItem(models.Model):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.po_id})"


class Receiving(models.Model):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='receivings')
    grn = models.CharField(max_length=100)
    invoice = models.CharField(max_length=100)
    document = models.FileField(upload_to='receipts/')
    matched = models.BooleanField(default=False)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receiving for PO#{self.po.id}"


class GoodsReceipt(models.Model):
    po_code = models.CharField(max_length=100)
    grn_code = models.CharField(max_length=100)
    invoice_code = models.CharField(max_length=100)
    match_success = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='grn_docs/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GRN {self.grn_code} for PO {self.po_code}"
