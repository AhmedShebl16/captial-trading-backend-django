# users/models.py

from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError


# User type choices
class UserTypes:
    ADMIN = 'admin'
    B2C_VISITOR = 'b2c_visitor'
    CORPORATE = 'corporate'
    HORECA = 'horeca'
    SUPPLIER = 'supplier'
    SUPPLIER_MERCHANT = 'supplier_merchant'
    STORAGE_CLIENT = 'storage_client'
    
    CHOICES = [
        (ADMIN, 'Admin (Super User)'),
        (B2C_VISITOR, 'B2C (Visitor)'),
        (CORPORATE, 'Corporate'),
        (HORECA, 'HoReCa'),
        (SUPPLIER, 'Supplier'),
        (SUPPLIER_MERCHANT, 'Supplier and Merchant'),
        (STORAGE_CLIENT, 'Storage Client'),
    ]


class UserManager(BaseUserManager):
    """
    Custom user model manager where username is the unique identifier
    for authentication instead of emails.
    """
    
    def get_queryset(self):
        """Return only non-deleted users by default"""
        return super().get_queryset().filter(is_deleted=False)
    
    def all_with_deleted(self):
        """Return all users including soft-deleted ones"""
        return super().get_queryset()
    
    def deleted_only(self):
        """Return only soft-deleted users"""
        return super().get_queryset().filter(is_deleted=True)

    def create_user(self, username, password=None, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        if not username:
            raise ValueError('The Username must be set')
        # Email is not the unique identifier, but let's normalize it if provided
        if 'email' in extra_fields:
            extra_fields['email'] = self.normalize_email(extra_fields['email'])
        
        # Set default role if not provided
        if 'role' not in extra_fields:
            extra_fields['role'] = UserTypes.B2C_VISITOR
            
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # A superuser might not need all these fields, but we set defaults
        extra_fields.setdefault('email', 'superuser@example.com')
        extra_fields.setdefault('first_name', 'Admin')
        extra_fields.setdefault('last_name', 'User')
        extra_fields.setdefault('role', UserTypes.ADMIN)

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with 7 different user types.
    """
    # Using a standard BigAutoField for the primary key `id` is good practice.
    id = models.BigAutoField(primary_key=True)
    # user_id is a separate, public-facing identifier.
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)  # Made nullable for flexibility
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # User type and role
    role = models.CharField(
        max_length=50, 
        choices=UserTypes.CHOICES,
        default=UserTypes.B2C_VISITOR,
        help_text="User type determines permissions and access levels"
    )
    
    # Additional fields for different user types
    company_name = models.CharField(max_length=200, blank=True, null=True, help_text="Company name for corporate users")
    business_type = models.CharField(max_length=100, blank=True, null=True, help_text="Type of business")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Contact phone number")
    address = models.TextField(blank=True, null=True, help_text="Business address")
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False, help_text="Whether the user account has been verified")
    
    # Password reset fields
    reset_otp = models.CharField(max_length=10, blank=True, null=True)
    reset_otp_expiry = models.DateTimeField(blank=True, null=True)
    
    # Soft delete fields
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    # Required fields for createsuperuser command
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def clean(self):
        """Validate the model before saving"""
        super().clean()
        
        # Validate role-specific requirements
        if self.role == UserTypes.CORPORATE and not self.company_name:
            raise ValidationError("Corporate users must provide a company name.")
        
        if self.role in [UserTypes.HORECA, UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT] and not self.business_type:
            raise ValidationError(f"{self.get_role_display()} users must provide a business type.")
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == UserTypes.ADMIN
    
    def is_corporate(self):
        """Check if user is a corporate user"""
        return self.role == UserTypes.CORPORATE
    
    def is_supplier(self):
        """Check if user is a supplier (including supplier merchant)"""
        return self.role in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT]
    
    def is_merchant(self):
        """Check if user is a merchant (supplier merchant only)"""
        return self.role == UserTypes.SUPPLIER_MERCHANT
    
    def is_storage_client(self):
        """Check if user is a storage client"""
        return self.role == UserTypes.STORAGE_CLIENT
    
    def is_visitor(self):
        """Check if user is a B2C visitor"""
        return self.role == UserTypes.B2C_VISITOR
    
    def is_horeca(self):
        """Check if user is a HoReCa user"""
        return self.role == UserTypes.HORECA
    
    def soft_delete(self):
        """Soft delete the user by setting is_deleted=True and deleted_at timestamp"""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['is_deleted', 'deleted_at', 'is_active'])
    
    def hard_delete(self):
        """Hard delete the user from the database"""
        self.delete()
    
    def restore(self):
        """Restore a soft-deleted user"""
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=['is_deleted', 'deleted_at', 'is_active'])

    class Meta:
        db_table = 'user'
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
