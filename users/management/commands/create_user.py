# users/management/commands/create_user.py

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from users.models import UserTypes
from users.utils import create_user_by_type

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a user with a specific role and required fields'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the new user')
        parser.add_argument('password', type=str, help='Password for the new user')
        parser.add_argument('role', type=str, choices=[choice[0] for choice in UserTypes.CHOICES], 
                          help='Role for the new user')
        parser.add_argument('--email', type=str, help='Email address')
        parser.add_argument('--first-name', type=str, help='First name')
        parser.add_argument('--last-name', type=str, help='Last name')
        parser.add_argument('--company-name', type=str, help='Company name (required for corporate users)')
        parser.add_argument('--business-type', type=str, help='Business type (required for business users)')
        parser.add_argument('--phone-number', type=str, help='Phone number')
        parser.add_argument('--address', type=str, help='Address')
        parser.add_argument('--verified', action='store_true', help='Mark user as verified')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        role = options['role']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            raise CommandError(f'User with username "{username}" already exists.')
        
        # Prepare extra fields
        extra_fields = {}
        
        if options['email']:
            extra_fields['email'] = options['email']
        if options['first_name']:
            extra_fields['first_name'] = options['first_name']
        if options['last_name']:
            extra_fields['last_name'] = options['last_name']
        if options['company_name']:
            extra_fields['company_name'] = options['company_name']
        if options['business_type']:
            extra_fields['business_type'] = options['business_type']
        if options['phone_number']:
            extra_fields['phone_number'] = options['phone_number']
        if options['address']:
            extra_fields['address'] = options['address']
        if options['verified']:
            extra_fields['is_verified'] = True
        
        try:
            # Create user using utility function
            user = create_user_by_type(username, password, role, **extra_fields)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created user "{username}" with role "{user.get_role_display()}"'
                )
            )
            
            # Display user details
            self.stdout.write(f'User ID: {user.user_id}')
            self.stdout.write(f'Role: {user.get_role_display()}')
            self.stdout.write(f'Email: {user.email or "Not provided"}')
            self.stdout.write(f'Verified: {user.is_verified}')
            
            if user.company_name:
                self.stdout.write(f'Company: {user.company_name}')
            if user.business_type:
                self.stdout.write(f'Business Type: {user.business_type}')
                
        except ValueError as e:
            raise CommandError(f'Validation error: {e}')
        except Exception as e:
            raise CommandError(f'Error creating user: {e}')
