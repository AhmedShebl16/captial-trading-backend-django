# users/utils.py

from django.contrib.auth import get_user_model
from .models import UserTypes

User = get_user_model()

def create_user_by_type(username, password, role, **extra_fields):
    """
    Create a user with specific role and required fields validation
    
    Args:
        username (str): Unique username
        password (str): User password
        role (str): User role from UserTypes
        **extra_fields: Additional user fields
    
    Returns:
        User: Created user instance
    
    Raises:
        ValueError: If required fields are missing for the role
    """
    
    # Validate role
    if role not in dict(UserTypes.CHOICES):
        raise ValueError(f"Invalid role: {role}")
    
    # Set role-specific defaults and validation
    if role == UserTypes.ADMIN:
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
    
    elif role == UserTypes.CORPORATE:
        if not extra_fields.get('company_name'):
            raise ValueError("Corporate users must provide a company_name")
        extra_fields.setdefault('is_verified', False)
    
    elif role in [UserTypes.HORECA, UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT]:
        if not extra_fields.get('business_type'):
            raise ValueError(f"{dict(UserTypes.CHOICES)[role]} users must provide a business_type")
        extra_fields.setdefault('is_verified', False)
    
    elif role == UserTypes.STORAGE_CLIENT:
        extra_fields.setdefault('is_verified', False)
    
    elif role == UserTypes.B2C_VISITOR:
        extra_fields.setdefault('is_verified', False)
    
    # Set role
    extra_fields['role'] = role
    
    # Create user
    user = User.objects.create_user(username=username, password=password, **extra_fields)
    return user

def get_users_by_role(role):
    """
    Get all users with a specific role
    
    Args:
        role (str): User role from UserTypes
    
    Returns:
        QuerySet: Users with the specified role
    """
    return User.objects.filter(role=role, is_deleted=False)

def get_verified_users():
    """Get all verified users"""
    return User.objects.filter(is_verified=True, is_deleted=False)

def get_unverified_users():
    """Get all unverified users"""
    return User.objects.filter(is_verified=False, is_deleted=False)

def get_business_users():
    """Get all business-related users (corporate, HoReCa, supplier, etc.)"""
    business_roles = [
        UserTypes.CORPORATE,
        UserTypes.HORECA,
        UserTypes.SUPPLIER,
        UserTypes.SUPPLIER_MERCHANT,
        UserTypes.STORAGE_CLIENT
    ]
    return User.objects.filter(role__in=business_roles, is_deleted=False)

def get_supplier_users():
    """Get all supplier users (supplier and supplier_merchant)"""
    supplier_roles = [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT]
    return User.objects.filter(role__in=supplier_roles, is_deleted=False)

def get_corporate_users():
    """Get all corporate users"""
    return User.objects.filter(role=UserTypes.CORPORATE, is_deleted=False)

def get_horeca_users():
    """Get all HoReCa users"""
    return User.objects.filter(role=UserTypes.HORECA, is_deleted=False)

def get_storage_clients():
    """Get all storage client users"""
    return User.objects.filter(role=UserTypes.STORAGE_CLIENT, is_deleted=False)

def get_visitor_users():
    """Get all B2C visitor users"""
    return User.objects.filter(role=UserTypes.B2C_VISITOR, is_deleted=False)

def verify_user(user_id):
    """
    Verify a user account
    
    Args:
        user_id: User ID or UUID
    
    Returns:
        bool: True if verification successful, False otherwise
    """
    try:
        if isinstance(user_id, str):
            user = User.objects.get(user_id=user_id)
        else:
            user = User.objects.get(id=user_id)
        
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        return True
    except User.DoesNotExist:
        return False

def change_user_role(user_id, new_role):
    """
    Change a user's role
    
    Args:
        user_id: User ID or UUID
        new_role (str): New role from UserTypes
    
    Returns:
        bool: True if role change successful, False otherwise
    """
    try:
        if isinstance(user_id, str):
            user = User.objects.get(user_id=user_id)
        else:
            user = User.objects.get(id=user_id)
        
        # Prevent changing admin role
        if user.role == UserTypes.ADMIN:
            return False
        
        # Validate new role
        if new_role not in dict(UserTypes.CHOICES):
            return False
        
        # Validate role-specific requirements
        if new_role == UserTypes.CORPORATE and not user.company_name:
            return False
        
        if new_role in [UserTypes.HORECA, UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT] and not user.business_type:
            return False
        
        user.role = new_role
        user.save(update_fields=['role'])
        return True
    except User.DoesNotExist:
        return False

def get_role_statistics():
    """
    Get statistics about user roles
    
    Returns:
        dict: Statistics about user roles
    """
    stats = {}
    for role_value, role_display in UserTypes.CHOICES:
        count = User.objects.filter(role=role_value, is_deleted=False).count()
        verified_count = User.objects.filter(role=role_value, is_verified=True, is_deleted=False).count()
        stats[role_value] = {
            'display': role_display,
            'total': count,
            'verified': verified_count,
            'unverified': count - verified_count
        }
    return stats
