from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q

from rest_framework import status, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenViewBase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    UserRegisterSerializer,
    UserLogoutSerializer,
    UserListSerializer,
    UserUpdateSerializer,
    MyTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer
)
from users.repository.repository import UserRepository
from users.services.password_reset_service import (
    PasswordResetRequestService, OTPVerificationService, PasswordChangeService, DjangoEmailSender
)
from users.services.registration_service import UserRegistrationService
from users.services.authentication_service import UserAuthenticationService
from users.services.user_update_service import UserUpdateService
from users.services.user_activation_service import UserActivationService
from users.services.user_delete_service import UserDeleteService

User = get_user_model()

# Dependency injection
user_repo = UserRepository()
registration_service = UserRegistrationService(user_repo)
authentication_service = UserAuthenticationService(user_repo)
user_update_service = UserUpdateService(user_repo)
user_activation_service = UserActivationService(user_repo)
user_delete_service = UserDeleteService(user_repo)
email_sender = DjangoEmailSender()
otp_verifier = OTPVerificationService(user_repo)
reset_request_service = PasswordResetRequestService(user_repo, email_sender)
password_change_service = PasswordChangeService(user_repo, otp_verifier)

# Custom permission class for OPTIONS requests
class AllowOptionsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return super().has_permission(request, view)

# --- Throttling Classes for Login ---
class LoginAnonThrottle(AnonRateThrottle):
    rate = '10/min'

class LoginUserThrottle(UserRateThrottle):
    rate = '60/min'

# --- API Views ---
@extend_schema(
    request=MyTokenObtainPairSerializer,
    responses={200: {'description': 'Login successful.'}},
    tags=['Authentication']
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([LoginAnonThrottle, LoginUserThrottle])
def login_view(request):
    serializer = MyTokenObtainPairSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    except Exception:
        return Response({'detail': 'No active account found with the given credentials'}, status=status.HTTP_401_UNAUTHORIZED)



@extend_schema(
    request=UserRegisterSerializer,
    responses={201: {'description': 'User registered successfully.'}},
    tags=['Authentication']
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user, error = registration_service.register(serializer.validated_data)
    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)

@extend_schema(
    request=UserLogoutSerializer,
    responses={200: {'description': 'Logout successful.'}},
    tags=['Authentication']
)
@csrf_exempt
@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    serializer = UserLogoutSerializer(data=request.data)
    if serializer.is_valid():
        try:
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['Users'],
    summary='User management operations',
    description='CRUD operations for user management including listing, creating, updating, and managing user status'
)
class UserViewSet(mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    lookup_field = 'user_id'

    @extend_schema(
        responses={200: UserListSerializer, 404: {'description': 'User not found'}},
        tags=['Users'],
        summary='Get user details',
        description='Retrieve detailed information about a specific user'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_permissions(self):
        """Allow OPTIONS requests without authentication for CORS preflight"""
        if self.request.method == 'OPTIONS':
            return [AllowOptionsPermission()]
        if self.action in ['create']:
            return [AllowAny()]
        return super().get_permissions()

    def get_authentication_classes(self):
        """Allow OPTIONS requests without authentication for CORS preflight"""
        if self.request.method == 'OPTIONS':
            return []
        return super().get_authentication_classes()

    @extend_schema(
        parameters=[
            OpenApiParameter(name='user', description='Filter by username or user_id', required=False, type=OpenApiTypes.STR),
        ],
        responses={200: UserListSerializer(many=True)},
        tags=['Users'],
        summary='List users',
        description='Get a list of all users with optional filtering by username or user_id'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        user_query = self.request.query_params.get('user', None)
        if user_query:
            return User.objects.filter(
                Q(username__icontains=user_query) |
                Q(user_id__icontains=user_query)
            )
        return User.objects.all()

    @extend_schema(
        request=UserRegisterSerializer,
        responses={201: {'description': 'User registered successfully'}, 400: {'description': 'Bad request'}},
        tags=['Users'],
        summary='Create new user',
        description='Register a new user account'
    )
    def create(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user, error = registration_service.register(serializer.validated_data)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer, 
            400: {
                'description': 'Bad request',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Validation error'}
                }
            }
        },
        tags=['Users'],
        summary='Update user',
        description='Update user information by user_id in URL'
    )
    def partial_update(self, request, user_id=None):
        user = self.get_object()
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='user_id', 
                description='UUID of the user to update', 
                required=True, 
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        request=UserUpdateSerializer,
        responses={
            200: UserListSerializer, 
            400: {
                'description': 'Bad request',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Validation error'}
                }
            },
            404: {
                'description': 'User not found',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'User not found'}
                }
            }
        },
        tags=['Users'],
        summary='Update user information',
        description='Update user information by user_id query parameter. Requires user_id as a query parameter.'
    )
    @action(detail=False, methods=['patch'], url_path='update', permission_classes=[IsAuthenticated])
    def update_user(self, request):
        user_id_param = request.query_params.get('user_id')
        if not user_id_param:
            return Response(
                {'error': "The 'user_id' query parameter is required for PATCH requests."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user, error = user_update_service.update(user_id_param, serializer.validated_data)
        if error:
            if "not found" in error.lower():
                return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        response_serializer = UserListSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: UserListSerializer(many=True)},
        tags=['Users'],
        summary='Get active users',
        description='Retrieve a list of all active users'
    )
    @action(detail=False, methods=['get'], url_path='active', permission_classes=[IsAuthenticated])
    def active_users(self, request):
        active_users = User.objects.filter(is_active=True)
        serializer = UserListSerializer(active_users, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='user_id', 
                description='UUID of the user to deactivate', 
                required=True, 
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        request=None,
        responses={
            200: {
                'description': 'User deactivated successfully',
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'User deactivated successfully.'}
                }
            },
            400: {
                'description': 'Bad request',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': "The 'user_id' query parameter is required."}
                }
            },
            404: {
                'description': 'User not found',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'User not found'}
                }
            }
        },
        tags=['Users'],
        summary='Deactivate user',
        description='Deactivate a user by user_id query parameter. Requires user_id as a query parameter.'
    )
    @action(detail=False, methods=['patch'], url_path='deactivate', permission_classes=[IsAuthenticated])
    def deactivate_user(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': "The 'user_id' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user, error = user_activation_service.deactivate(user_id)
        if error:
            if "not found" in error.lower():
                return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'User deactivated successfully.'}, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='user_id', 
                description='UUID of the user to soft delete', 
                required=True, 
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        request=None,
        responses={
            200: {
                'description': 'User soft deleted successfully',
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'User soft deleted successfully.'}
                }
            },
            400: {
                'description': 'Bad request',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': "The 'user_id' query parameter is required."}
                }
            },
            404: {
                'description': 'User not found',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'User not found'}
                }
            }
        },
        tags=['Users'],
        summary='Soft delete user',
        description='Soft delete a user by setting is_deleted=True and deleted_at timestamp. Requires user_id as a query parameter.'
    )
    @action(detail=False, methods=['patch'], url_path='soft-delete', permission_classes=[IsAuthenticated])
    def soft_delete_user(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': "The 'user_id' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user, error = user_delete_service.soft_delete(user_id)
        if error:
            if "not found" in error.lower():
                return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'User soft deleted successfully.'}, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='user_id', 
                description='UUID of the user to hard delete', 
                required=True, 
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        request=None,  # DELETE requests typically don't have a request body
        responses={
            200: {
                'description': 'User hard deleted successfully',
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'User hard deleted successfully.'}
                }
            },
            400: {
                'description': 'Bad request',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': "The 'user_id' query parameter is required."}
                }
            },
            404: {
                'description': 'User not found',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'User not found'}
                }
            }
        },
        tags=['Users'],
        summary='Hard delete user',
        description='Permanently delete a user from the database (irreversible). Requires user_id as a query parameter.'
    )
    @action(detail=False, methods=['delete'], url_path='hard-delete', permission_classes=[IsAuthenticated])
    def hard_delete_user(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': "The 'user_id' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        success, error = user_delete_service.hard_delete(user_id)
        if error:
            if "not found" in error.lower():
                return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'User hard deleted successfully.'}, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='user_id', 
                description='UUID of the user to restore', 
                required=True, 
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        request=None,
        responses={
            200: {
                'description': 'User restored successfully',
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'User restored successfully.'}
                }
            },
            400: {
                'description': 'Bad request',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': "The 'user_id' query parameter is required."}
                }
            },
            404: {
                'description': 'User not found',
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'User not found'}
                }
            }
        },
        tags=['Users'],
        summary='Restore user',
        description='Restore a soft-deleted user. Requires user_id as a query parameter.'
    )
    @action(detail=False, methods=['patch'], url_path='restore', permission_classes=[IsAuthenticated])
    def restore_user(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': "The 'user_id' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        user, error = user_delete_service.restore(user_id)
        if error:
            if "not found" in error.lower():
                return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'User restored successfully.'}, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            200: {
                'description': 'List of all supplier users',
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'user_id': {'type': 'string', 'format': 'uuid'},
                        'username': {'type': 'string'},
                        'email': {'type': 'string'},
                        'first_name': {'type': 'string'},
                        'last_name': {'type': 'string'},
                        'role': {'type': 'string'},
                        'role_display': {'type': 'string'},
                        'company_name': {'type': 'string'},
                        'business_type': {'type': 'string'},
                        'phone_number': {'type': 'string'},
                        'address': {'type': 'string'},
                        'is_verified': {'type': 'boolean'},
                        'created_at': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        },
        tags=['Users'],
        summary='Get all supplier users',
        description='Get a list of all users with supplier roles (supplier and supplier_merchant). Accessible by anyone.'
    )
    @action(detail=False, methods=['get'], url_path='suppliers', permission_classes=[AllowAny])
    def get_suppliers(self, request):
        """Get all supplier users (supplier and supplier_merchant roles)"""
        from .models import UserTypes
        
        suppliers = User.objects.filter(
            role__in=[UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT],
            is_deleted=False,
            is_active=True
        ).order_by('-created_at')
        
        serializer = UserListSerializer(suppliers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PasswordResetViewSet(viewsets.ViewSet):
    """
    ViewSet for password reset operations.
    """
    serializer_class = ForgotPasswordSerializer  # Default serializer for OpenAPI schema
    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={200: {'description': 'If the email exists, an OTP has been sent.'}},
        tags=['Password Reset']
    )
    @action(detail=False, methods=['post'], url_path='forgot-password', permission_classes=[AllowAny])
    def forgot_password(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        reset_request_service.request_reset(serializer.validated_data['email'])
        return Response({'message': 'If the email exists, an OTP has been sent.'}, status=status.HTTP_200_OK)

    @extend_schema(
        request=VerifyOTPSerializer,
        responses={200: {'description': 'OTP is valid.'}},
        tags=['Password Reset']
    )
    @action(detail=False, methods=['post'], url_path='verify-otp', permission_classes=[AllowAny])
    def verify_otp(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        valid = otp_verifier.verify_otp(
            serializer.validated_data['email'],
            serializer.validated_data['otp']
        )
        if valid:
            return Response({'message': 'OTP is valid.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=ResetPasswordSerializer,
        responses={200: {'description': 'Password reset successful.'}},
        tags=['Password Reset']
    )
    @action(detail=False, methods=['post'], url_path='reset-password', permission_classes=[AllowAny])
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        success = password_change_service.change_password(
            serializer.validated_data['email'],
            serializer.validated_data['otp'],
            serializer.validated_data['new_password']
        )
        if success:
            return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP or password.'}, status=status.HTTP_400_BAD_REQUEST)
