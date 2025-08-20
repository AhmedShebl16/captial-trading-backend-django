from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'email', 'username', 'password', 'first_name', 'last_name', 'role', 'created_at']
        read_only_fields = ['user_id', 'created_at']
    
    # Remove the create method since we're using the service layer for user creation

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
    def validate_refresh(self, value):
        """
        Validate that the refresh token has a valid format
        """
        if not value:
            raise serializers.ValidationError("Refresh token is required.")
        
        # Basic validation - check if it looks like a JWT
        parts = value.split('.')
        if len(parts) != 3:
            raise serializers.ValidationError("Invalid token format.")
            
        return value

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['id'] = self.user.id
        data['user_id'] = str(self.user.user_id)
        return data

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'email', 'username', 'first_name', 'last_name', 'role', 'created_at', 'is_active', 'is_deleted', 'deleted_at']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role']
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'role': {'required': False},
        }

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)
    new_password = serializers.CharField(write_only=True, min_length=6)