from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


class ProtectedSwaggerView(SpectacularSwaggerView):
    """
    Protected Swagger UI view that requires authentication.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated via session
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        
        # Check for JWT token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)
                if user and user.is_authenticated:
                    request.user = user
                    return super().dispatch(request, *args, **kwargs)
            except (InvalidToken, TokenError):
                pass
        
        # Check for JWT token in cookies
        token = request.COOKIES.get('access_token') or request.COOKIES.get('jwt_token')
        if token:
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)
                if user and user.is_authenticated:
                    request.user = user
                    return super().dispatch(request, *args, **kwargs)
            except (InvalidToken, TokenError):
                pass
        
        # No valid authentication found, show login form
        return render(request, 'core/docs_login.html', {
            'next': request.path,
            'login_url': '/api/v1/auth/login/'
        })


class ProtectedRedocView(SpectacularRedocView):
    """
    Protected ReDoc view that requires authentication.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated via session
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        
        # Check for JWT token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)
                if user and user.is_authenticated:
                    request.user = user
                    return super().dispatch(request, *args, **kwargs)
            except (InvalidToken, TokenError):
                pass
        
        # Check for JWT token in cookies
        token = request.COOKIES.get('access_token') or request.COOKIES.get('jwt_token')
        if token:
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)
                if user and user.is_authenticated:
                    request.user = user
                    return super().dispatch(request, *args, **kwargs)
            except (InvalidToken, TokenError):
                pass
        
        # No valid authentication found, show login form
        return render(request, 'core/docs_login.html', {
            'next': request.path,
            'login_url': '/api/v1/auth/login/'
        })


class ProtectedSchemaView(SpectacularAPIView):
    """
    Protected API schema view that requires authentication.
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated via session
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        
        # Check for JWT token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)
                if user and user.is_authenticated:
                    request.user = user
                    return super().dispatch(request, *args, **kwargs)
            except (InvalidToken, TokenError):
                pass
        
        # Check for JWT token in cookies
        token = request.COOKIES.get('access_token') or request.COOKIES.get('jwt_token')
        if token:
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)
                if user and user.is_authenticated:
                    request.user = user
                    return super().dispatch(request, *args, **kwargs)
            except (InvalidToken, TokenError):
                pass
        
        # No valid authentication found, redirect to login
        return HttpResponseRedirect('/api/v1/auth/login/')
