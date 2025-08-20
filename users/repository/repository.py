import uuid
from typing import Optional, List
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class UserRepository:
    """
    Repository class to handle all database operations for User model.
    Provides an abstraction layer between the service layer and data access.
    """

    def get_all(self) -> List[User]:
        """
        Retrieve all users from the database.
        
        Returns:
            List[User]: All user instances
        """
        return User.objects.all()

    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by their UUID.
        
        Args:
            user_id (str): UUID string of the user
            
        Returns:
            Optional[User]: User instance if found, None otherwise
        """
        try:
            # Validate if the provided id is a valid UUID
            uuid.UUID(user_id, version=4)
            return User.objects.get(user_id=user_id)
        except (ValueError, User.DoesNotExist):
            return None

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by their username.
        
        Args:
            username (str): Username of the user
            
        Returns:
            Optional[User]: User instance if found, None otherwise
        """
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email.
        
        Args:
            email (str): Email of the user
            
        Returns:
            Optional[User]: User instance if found, None otherwise
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def search_users(self, query: str) -> List[User]:
        """
        Search users by username or user_id.
        
        Args:
            query (str): Search query string
            
        Returns:
            List[User]: Users matching the search criteria
        """
        return User.objects.filter(
            Q(username__icontains=query) | Q(user_id__icontains=query)
        )

    def create_user(self, **kwargs) -> User:
        """
        Create a new user with the provided data.
        
        Args:
            **kwargs: User field data
            
        Returns:
            User: The created user instance
        """
        return User.objects.create_user(**kwargs)

    def update(self, user: User, **kwargs) -> User:
        """
        Update an existing user with the provided data.
        
        Args:
            user (User): The user instance to update
            **kwargs: Updated field data
            
        Returns:
            User: The updated user instance
        """
        # Update regular fields
        for field, value in kwargs.items():
            # Skip password field as it needs special handling
            if field != 'password':
                setattr(user, field, value)
        
        # Handle password separately if provided
        if 'password' in kwargs:
            user.set_password(kwargs['password'])
        
        user.save()
        return user

    def delete(self, user: User) -> bool:
        """
        Delete a user from the database.
        
        Args:
            user (User): The user instance to delete
            
        Returns:
            bool: True if deleted successfully
        """
        user.delete()
        return True

    def exists_by_username(self, username: str) -> bool:
        """
        Check if a user with the given username already exists.
        
        Args:
            username (str): Username to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        return User.objects.filter(username=username).exists()

    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user with the given email already exists.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        return User.objects.filter(email=email).exists()

    def filter_by_role(self, role: str) -> List[User]:
        """
        Get all users with a specific role.
        
        Args:
            role (str): Role to filter by
            
        Returns:
            List[User]: Users with the specified role
        """
        return User.objects.filter(role=role)

    def get_active_users(self) -> List[User]:
        """
        Get all active users.
        
        Returns:
            List[User]: All active users
        """
        return User.objects.filter(is_active=True)

    def get_staff_users(self) -> List[User]:
        """
        Get all staff users.
        
        Returns:
            List[User]: All staff users
        """
        return User.objects.filter(is_staff=True) 