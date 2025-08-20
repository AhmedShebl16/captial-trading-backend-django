from .interfaces import IUserRegistrationService

class UserRegistrationService(IUserRegistrationService):
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def register(self, data: dict):
        # Registration logic (example, adapt as needed)
        if self.user_repo.exists_by_username(data['username']):
            return None, 'Username already exists.'
        if 'email' in data and self.user_repo.exists_by_email(data['email']):
            return None, 'Email already exists.'
        user = self.user_repo.create_user(**data)
        return user, None 