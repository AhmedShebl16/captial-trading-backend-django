from abc import ABC, abstractmethod

class IUserRegistrationService(ABC):
    @abstractmethod
    def register(self, data: dict):
        pass

class IUserAuthenticationService(ABC):
    @abstractmethod
    def authenticate(self, username: str, password: str):
        pass

class IUserUpdateService(ABC):
    @abstractmethod
    def update(self, user_id: str, data: dict):
        pass

class IUserActivationService(ABC):
    @abstractmethod
    def activate(self, user_id: str):
        pass

    @abstractmethod
    def deactivate(self, user_id: str):
        pass

class IUserDeleteService(ABC):
    @abstractmethod
    def soft_delete(self, user_id: str):
        pass

    @abstractmethod
    def hard_delete(self, user_id: str):
        pass

    @abstractmethod
    def restore(self, user_id: str):
        pass 