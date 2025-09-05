# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.conf import settings

ROLE_LEVELS = {
    "staff": 1,
    "finance_manager": 2,
    "operations_manager": 3,
    "md": 4,
    "admin": 5,
}

# Custom Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='staff', **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, role='admin', **extra_fields)

# Role choices
ROLE_CHOICES = (
    ('staff', 'Staff'),
    ('finance_manager', 'Finance Manager'),
    ('operations_manager', 'Operations Manager'),
    ('md', 'Managing Director'),
    ('admin', 'Admin'),
)

# Custom User
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    full_name = models.CharField(max_length=100, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    EMAIL_FIELD = 'email'

    def __str__(self):
        return self.email

# Profile Image Upload Path
def profile_image_upload_path(instance, filename):
    return f'profile_images/user_{instance.user.id}/{filename}'

# User Profile model
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    profile_image = models.ImageField(upload_to=profile_image_upload_path, blank=True, null=True)

    def __str__(self):
        return self.full_name or self.user.email

# Page-based permission
class PagePermission(models.Model):
    page_name = models.CharField(max_length=100, unique=True)
    min_role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='staff')

    def __str__(self):
        return f"Page: {self.page_name} requires {self.min_role}+"

# Action-based permission
class ActionPermission(models.Model):
    action_name = models.CharField(max_length=100, unique=True)
    min_role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='staff')

    def __str__(self):
        return f"Action: {self.action_name} requires {self.min_role}+"

# App-specific permission lists with role mappings
PERMISSION_ROLES = {
    'default': 'staff',
    'product_documentation': 'finance_manager',
    'delete_product_inflow': 'admin',
    'delete_product_outflow': 'admin',
    'warehouse': 'finance_manager',  # Added for warehouse app
}

INVENTORY_PAGES = ['inventory_metrics', 'storage_bins', 'expired_items', 'items', 'stock_records', 'expiry_tracked_items']
INVENTORY_ACTIONS = [
    'create_storage_bin', 'create_item', 'create_stock_record', 'create_expiry_tracked_item',
    'update_storage_bin', 'update_item', 'update_stock_record', 'update_expiry_tracked_item',
    'delete_item', 'delete_storage_bin', 'delete_stock_record', 'delete_expiry_tracked_item'
]

PROCUREMENT_PAGES = [
    "requisitions", "purchase_orders", "po_items", "receiving", "goods_receipts", "vendors",
]

PROCUREMENT_ACTIONS = [
    "create_requisition", "approve_requisition", "create_purchase_order", "approve_purchase_order",
    "create_po_item", "create_receiving", "create_goods_receipt", "add_vendor", "delete_vendor",
    "update_requisition", "delete_requisition", "update_purchase_order", "delete_purchase_order",
    "update_po_item", "delete_po_item", "update_receiving", "delete_receiving",
    "update_goods_receipt", "delete_goods_receipt"
]

RECEIPT_PAGES = ["receipt_archive", "stock_receipts", "signing_receipts"]
RECEIPT_ACTIONS = ["create_receipt", "create_stock_receipt", "create_signing_receipt"]

FINANCE_PAGES = ["finance_categories", "finance_transactions", "finance_overview"]
FINANCE_ACTIONS = [
    "create_finance_category", "create_finance_transaction",
    "update_finance_category", "delete_finance_category",
    "update_finance_transaction", "delete_finance_transaction",
]

RENTALS_PAGES = ["rentals_active", "rentals_equipment", "rentals_payments"]
RENTALS_ACTIONS = ["create_rental", "update_rental", "delete_rental", "create_equipment", "create_payment"]

ANALYTICS_PAGES = ["analytics_dwell", "analytics_eoq", "analytics_stock"]
ANALYTICS_ACTIONS = ["create_dwell", "create_eoq", "create_stock_analytics"]

PRODUCT_DOCUMENTATION_PAGES = ["product_documentation", "product_inflow", "product_outflow"]
PRODUCT_DOCUMENTATION_ACTIONS = [
    "create_product_inflow", "update_product_inflow", "delete_product_inflow",
    "create_product_outflow", "update_product_outflow", "delete_product_outflow",
]

WAREHOUSE_PAGES = ['warehouse']
WAREHOUSE_ACTIONS = ['create_warehouse_item', 'update_warehouse_item', 'delete_warehouse_item']

ALL_PAGES = (
    INVENTORY_PAGES + PROCUREMENT_PAGES + RECEIPT_PAGES + FINANCE_PAGES +
    RENTALS_PAGES + ANALYTICS_PAGES + PRODUCT_DOCUMENTATION_PAGES + WAREHOUSE_PAGES
)
ALL_ACTIONS = (
    INVENTORY_ACTIONS + PROCUREMENT_ACTIONS + RECEIPT_ACTIONS + FINANCE_ACTIONS +
    RENTALS_ACTIONS + ANALYTICS_ACTIONS + PRODUCT_DOCUMENTATION_ACTIONS + WAREHOUSE_ACTIONS
)