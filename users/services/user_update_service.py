from .interfaces import IUserUpdateService

class UserUpdateService(IUserUpdateService):
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def update(self, user_id: str, data: dict):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None, 'User not found.'
        # Example: update fields
        for field, value in data.items():
            setattr(user, field, value)
        user.save()
        return user, None 