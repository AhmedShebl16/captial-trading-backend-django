from .interfaces import IUserActivationService

class UserActivationService(IUserActivationService):
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def activate(self, user_id: str):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None, 'User not found.'
        user.is_active = True
        user.save()
        return user, None

    def deactivate(self, user_id: str):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None, 'User not found.'
        user.is_active = False
        user.save()
        return user, None 