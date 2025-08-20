from .interfaces import IUserAuthenticationService

class UserAuthenticationService(IUserAuthenticationService):
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def authenticate(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)
        if user and user.check_password(password):
            if not user.is_active:
                return None
            return user
        return None 