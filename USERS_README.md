# User Management System

This Django application implements a comprehensive user management system with 7 different user types, each with specific roles, permissions, and requirements.

## User Types

### 1. Admin (Super User)
- **Role**: `admin`
- **Description**: System administrators with full access
- **Features**: 
  - Full system access
  - User management capabilities
  - Can create, modify, and delete any user
- **Required Fields**: Username, password
- **Default Status**: Verified, Staff, Superuser

### 2. B2C (Visitor)
- **Role**: `b2c_visitor`
- **Description**: Individual consumers/visitors
- **Features**: 
  - Basic access to public features
  - Limited permissions
- **Required Fields**: Username, password
- **Default Status**: Unverified

### 3. Corporate
- **Role**: `corporate`
- **Description**: Business entities and corporations
- **Features**: 
  - Business-specific features
  - Corporate account management
- **Required Fields**: Username, password, company_name
- **Default Status**: Unverified

### 4. HoReCa
- **Role**: `horeca`
- **Description**: Hotels, Restaurants, and Cafes
- **Features**: 
  - Hospitality industry features
  - Business management tools
- **Required Fields**: Username, password, business_type
- **Default Status**: Unverified

### 5. Supplier
- **Role**: `supplier`
- **Description**: Product/service suppliers
- **Features**: 
  - Supplier management tools
  - Inventory management
- **Required Fields**: Username, password, business_type
- **Default Status**: Unverified

### 6. Supplier and Merchant
- **Role**: `supplier_merchant`
- **Description**: Users who are both suppliers and merchants
- **Features**: 
  - Combined supplier and merchant capabilities
  - Advanced business tools
- **Required Fields**: Username, password, business_type
- **Default Status**: Unverified

### 7. Storage Client
- **Role**: `storage_client`
- **Description**: Storage facility clients
- **Features**: 
  - Storage management tools
  - Client-specific features
- **Required Fields**: Username, password
- **Default Status**: Unverified

## Database Schema

The User model includes the following fields:

### Core Fields
- `id`: Primary key (BigAutoField)
- `user_id`: UUID identifier
- `username`: Unique username
- `email`: Email address (optional)
- `first_name`: First name
- `last_name`: Last name
- `password`: Hashed password
- `created_at`: Account creation timestamp

### Role and Status
- `role`: User type (choices from UserTypes)
- `is_active`: Account active status
- `is_staff`: Staff status
- `is_superuser`: Superuser status
- `is_verified`: Account verification status

### Business Information
- `company_name`: Company name (required for corporate users)
- `business_type`: Type of business (required for business users)
- `phone_number`: Contact phone number
- `address`: Business address

### System Fields
- `deleted_at`: Soft delete timestamp
- `is_deleted`: Soft delete flag
- `reset_otp`: Password reset OTP
- `reset_otp_expiry`: OTP expiration time

## Usage Examples

### Creating Users

#### Using Django Admin
1. Access Django admin interface
2. Navigate to Users section
3. Click "Add User"
4. Fill in required fields based on user type
5. Save the user

#### Using Management Command
```bash
# Create a corporate user
python manage.py create_user corporate_user password123 corporate \
    --email corporate@example.com \
    --first-name John \
    --last-name Doe \
    --company-name "ABC Corporation" \
    --phone-number "+1234567890" \
    --address "123 Business St, City, State"

# Create a HoReCa user
python manage.py create_user horeca_user password123 horeca \
    --email horeca@example.com \
    --first-name Jane \
    --last-name Smith \
    --business-type "Restaurant" \
    --phone-number "+1234567890"

# Create a supplier user
python manage.py create_user supplier_user password123 supplier \
    --email supplier@example.com \
    --business-type "Food Supplier" \
    --verified
```

#### Using Python Code
```python
from users.utils import create_user_by_type
from users.models import UserTypes

# Create a corporate user
user = create_user_by_type(
    username="corporate_user",
    password="password123",
    role=UserTypes.CORPORATE,
    email="corporate@example.com",
    company_name="ABC Corporation",
    first_name="John",
    last_name="Doe"
)

# Create a HoReCa user
user = create_user_by_type(
    username="horeca_user",
    password="password123",
    role=UserTypes.HORECA,
    email="horeca@example.com",
    business_type="Restaurant",
    first_name="Jane",
    last_name="Smith"
)
```

### Querying Users

```python
from users.utils import (
    get_users_by_role, get_corporate_users, get_supplier_users,
    get_business_users, get_verified_users
)

# Get all corporate users
corporate_users = get_corporate_users()

# Get all supplier users (including supplier merchants)
supplier_users = get_supplier_users()

# Get all business users
business_users = get_business_users()

# Get all verified users
verified_users = get_verified_users()

# Get users by specific role
horeca_users = get_users_by_role(UserTypes.HORECA)
```

### User Validation

The system automatically validates user data based on their role:

```python
# This will raise a ValidationError
user = create_user_by_type(
    username="invalid_corporate",
    password="password123",
    role=UserTypes.CORPORATE
    # Missing company_name - will fail validation
)

# This will raise a ValidationError
user = create_user_by_type(
    username="invalid_supplier",
    password="password123",
    role=UserTypes.SUPPLIER
    # Missing business_type - will fail validation
)
```

### Role Checking

```python
# Check user roles
if user.is_admin():
    print("User is an admin")
elif user.is_corporate():
    print("User is a corporate user")
elif user.is_supplier():
    print("User is a supplier")
elif user.is_merchant():
    print("User is a merchant (supplier and merchant)")
elif user.is_storage_client():
    print("User is a storage client")
elif user.is_visitor():
    print("User is a B2C visitor")
elif user.is_horeca():
    print("User is a HoReCa user")
```

## API Endpoints

The system provides REST API endpoints for user management:

- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User authentication
- `GET /api/users/` - List users (with role-based filtering)
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Soft delete user
- `POST /api/users/{id}/verify/` - Verify user account
- `PUT /api/users/{id}/role/` - Change user role

## Security Features

- **Role-based Access Control**: Different permissions for different user types
- **Account Verification**: Users can be marked as verified/unverified
- **Soft Delete**: Users are soft-deleted rather than permanently removed
- **Password Security**: Secure password hashing and reset mechanisms
- **Input Validation**: Role-specific field validation

## Migration

To apply the database changes:

```bash
python manage.py makemigrations users
python manage.py migrate
```

## Testing

Run the test suite to ensure everything works correctly:

```bash
python manage.py test users
```

## Future Enhancements

- Role-based permissions system
- User groups and hierarchies
- Advanced business relationship management
- Audit logging for user actions
- Multi-tenant support
- API rate limiting based on user type
