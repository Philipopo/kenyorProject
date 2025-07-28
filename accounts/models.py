from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.conf import settings

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
    ('staff', 'Staff'),                    # Level 1
    ('finance_manager', 'Finance Manager'),# Level 2
    ('operations_manager', 'Operations Manager'),  # Level 3
    ('md', 'Managing Director'),           # Level 4
    ('admin', 'Admin'),                    # Full access
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
