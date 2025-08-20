from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PasswordResetViewSet, UserViewSet, logout_view, login_view

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'password-reset', PasswordResetViewSet, basename='password-reset')

urlpatterns = [
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('', include(router.urls)),
]