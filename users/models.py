# users/models.py

from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


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
        extra_fields.setdefault('role', 'admin')

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model.
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
    role = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
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
        return self.username
    
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
