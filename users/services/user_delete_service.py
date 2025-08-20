from .interfaces import IUserDeleteService
from users.repository.repository import UserRepository
from django.contrib.auth import get_user_model

User = get_user_model()


class UserDeleteService(IUserDeleteService):
    """
    Service for handling user deletion operations.
    Implements soft delete, hard delete, and restore functionality.
    """
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def soft_delete(self, user_id: str):
        """
        Soft delete a user by setting is_deleted=True and deleted_at timestamp.
        
        Args:
            user_id (str): The UUID of the user to soft delete
            
        Returns:
            tuple: (user, error) - user object if successful, error message if failed
        """
        try:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return None, "User not found"
            
            if user.is_deleted:
                return None, "User is already deleted"
            
            user.soft_delete()
            return user, None
            
        except Exception as e:
            return None, f"Error soft deleting user: {str(e)}"
    
    def hard_delete(self, user_id: str):
        """
        Permanently delete a user from the database.
        
        Args:
            user_id (str): The UUID of the user to hard delete
            
        Returns:
            tuple: (success, error) - True if successful, error message if failed
        """
        try:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return False, "User not found"
            
            user.hard_delete()
            return True, None
            
        except Exception as e:
            return False, f"Error hard deleting user: {str(e)}"
    
    def restore(self, user_id: str):
        """
        Restore a soft-deleted user.
        
        Args:
            user_id (str): The UUID of the user to restore
            
        Returns:
            tuple: (user, error) - user object if successful, error message if failed
        """
        try:
            # Use all_with_deleted to include soft-deleted users
            user = User.objects.all_with_deleted().filter(user_id=user_id).first()
            if not user:
                return None, "User not found"
            
            if not user.is_deleted:
                return None, "User is not deleted"
            
            user.restore()
            return user, None
            
        except Exception as e:
            return None, f"Error restoring user: {str(e)}"
