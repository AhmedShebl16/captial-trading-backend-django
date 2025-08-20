from abc import ABC, abstractmethod
from django.utils import timezone
import random

class IPasswordResetRequestService(ABC):
    @abstractmethod
    def request_reset(self, email: str) -> bool:
        pass

class IOTPVerificationService(ABC):
    @abstractmethod
    def verify_otp(self, email: str, otp: str) -> bool:
        pass

class IPasswordChangeService(ABC):
    @abstractmethod
    def change_password(self, email: str, otp: str, new_password: str) -> bool:
        pass

class IEmailSender(ABC):
    @abstractmethod
    def send_otp_email(self, to_email: str, otp: str):
        pass

class PasswordResetRequestService(IPasswordResetRequestService):
    def __init__(self, user_repo, email_sender):
        self.user_repo = user_repo
        self.email_sender = email_sender

    def request_reset(self, email: str) -> bool:
        user = self.user_repo.get_by_email(email)
        if not user:
            return False
        otp = str(random.randint(100000, 999999))
        user.reset_otp = otp
        user.reset_otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
        user.save()
        self.email_sender.send_otp_email(user.email, otp)
        return True

class OTPVerificationService(IOTPVerificationService):
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def verify_otp(self, email: str, otp: str) -> bool:
        user = self.user_repo.get_by_email(email)
        if not user or not user.reset_otp or not user.reset_otp_expiry:
            return False
        if user.reset_otp != otp:
            return False
        if timezone.now() > user.reset_otp_expiry:
            return False
        return True

class PasswordChangeService(IPasswordChangeService):
    def __init__(self, user_repo, otp_verifier):
        self.user_repo = user_repo
        self.otp_verifier = otp_verifier

    def change_password(self, email: str, otp: str, new_password: str) -> bool:
        if not self.otp_verifier.verify_otp(email, otp):
            return False
        user = self.user_repo.get_by_email(email)
        user.set_password(new_password)
        user.reset_otp = None
        user.reset_otp_expiry = None
        user.save()
        return True

class DjangoEmailSender(IEmailSender):
    def send_otp_email(self, to_email: str, otp: str):
        from django.core.mail import send_mail
        send_mail(
            subject='My Calls Password Reset OTP',
            message=f'Your OTP code is: {otp}',
            from_email='remafactory72@gmail.com',
            recipient_list=[to_email],
            fail_silently=False,
        ) 