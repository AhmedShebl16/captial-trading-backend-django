from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import UserTypes

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'username', 'password', 'first_name', 'last_name', 
            'role', 'company_name', 'business_type', 'phone_number', 'address', 
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
    
    def validate(self, attrs):
        """Validate role-specific requirements"""
        role = attrs.get('role', UserTypes.B2C_VISITOR)
        
        # Validate corporate users have company name
        if role == UserTypes.CORPORATE and not attrs.get('company_name'):
            raise serializers.ValidationError(
                "Corporate users must provide a company name."
            )
        
        # Validate business users have business type
        if role in [UserTypes.HORECA, UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT]:
            if not attrs.get('business_type'):
                raise serializers.ValidationError(
                    f"{dict(UserTypes.CHOICES)[role]} users must provide a business type."
                )
        
        return attrs
    
    def create(self, validated_data):
        """Create user with role-specific defaults"""
        # Set default role if not provided
        if 'role' not in validated_data:
            validated_data['role'] = UserTypes.B2C_VISITOR
        
        # Create user using the manager
        user = User.objects.create_user(**validated_data)
        return user

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
        # Add user role to token
        token['role'] = user.role
        token['is_verified'] = user.is_verified
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['id'] = self.user.id
        data['user_id'] = str(self.user.user_id)
        data['role'] = self.user.role
        data['role_display'] = self.user.get_role_display()
        data['is_verified'] = self.user.is_verified
        return data

class UserListSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'username', 'first_name', 'last_name', 
            'role', 'role_display', 'company_name', 'business_type', 
            'phone_number', 'address', 'created_at', 'is_active', 
            'is_verified', 'is_deleted', 'deleted_at'
        ]

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'role', 'company_name', 
            'business_type', 'phone_number', 'address'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'role': {'required': False},
            'company_name': {'required': False},
            'business_type': {'required': False},
            'phone_number': {'required': False},
            'address': {'required': False},
        }
    
    def validate(self, attrs):
        """Validate role-specific requirements when updating"""
        role = attrs.get('role')
        if role:
            # Validate corporate users have company name
            if role == UserTypes.CORPORATE and not attrs.get('company_name'):
                # Check if user already has company_name
                if not self.instance.company_name:
                    raise serializers.ValidationError(
                        "Corporate users must provide a company name."
                    )
            
            # Validate business users have business type
            if role in [UserTypes.HORECA, UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT]:
                if not attrs.get('business_type') and not self.instance.business_type:
                    raise serializers.ValidationError(
                        f"{dict(UserTypes.CHOICES)[role]} users must provide a business type."
                    )
        
        return attrs

class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for updating user role only"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['role', 'role_display']
    
    def validate_role(self, value):
        """Validate role change"""
        if self.instance and self.instance.role == UserTypes.ADMIN:
            raise serializers.ValidationError("Cannot change admin user role.")
        return value

class UserVerificationSerializer(serializers.ModelSerializer):
    """Serializer for user verification"""
    class Meta:
        model = User
        fields = ['is_verified']

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)
    new_password = serializers.CharField(write_only=True, min_length=6)