from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Product, ProductCategory, ProductImage
from .serializers import (
    ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductSearchSerializer,
    ProductCategorySerializer, ProductImageSerializer
)
from users.models import UserTypes

User = get_user_model()


class ProductPagination(PageNumberPagination):
    """Custom pagination for products"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product management with role-based access control
    """
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        elif self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve', 'search', 'by_category', 'by_supplier']:
            return [AllowAny()]  # Anyone can view products
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]  # Only authenticated users can modify
        return super().get_permissions()
    
    def get_queryset(self):
        """Filter queryset based on user role and request parameters"""
        queryset = Product.objects.filter(is_deleted=False)
        
        # Filter by availability
        available_only = self.request.query_params.get('available_only', 'true').lower() == 'true'
        if available_only:
            queryset = queryset.filter(is_available=True)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Filter by supplier
        supplier = self.request.query_params.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier__username__icontains=supplier)
        
        # Filter by price range (based on user role)
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price or max_price:
            # Get the appropriate price field based on user role
            user = self.request.user
            if user.is_authenticated:
                if user.role == UserTypes.B2C_VISITOR:
                    price_field = 'end_user_price'
                elif user.role == UserTypes.CORPORATE:
                    price_field = 'retail_price_corporate'
                elif user.role == UserTypes.HORECA:
                    price_field = 'retail_price_horeca'
                elif user.role in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT]:
                    price_field = 'wholesale_price'
                else:
                    price_field = 'end_user_price'
                
                if min_price:
                    queryset = queryset.filter(**{f"{price_field}__gte": min_price})
                if max_price:
                    queryset = queryset.filter(**{f"{price_field}__lte": max_price})
            else:
                # For anonymous users, use end user price
                if min_price:
                    queryset = queryset.filter(end_user_price__gte=min_price)
                if max_price:
                    queryset = queryset.filter(end_user_price__lte=max_price)
        
        return queryset
    
    @extend_schema(
        responses={200: ProductListSerializer(many=True)},
        tags=['Products'],
        summary='List products',
        description='Get a list of all available products with role-based pricing'
    )
    def list(self, request, *args, **kwargs):
        """List products with role-based pricing"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        responses={200: ProductDetailSerializer},
        tags=['Products'],
        summary='Get product details',
        description='Get detailed information about a specific product with role-based pricing'
    )
    def retrieve(self, request, *args, **kwargs):
        """Get product details with role-based pricing"""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        request=ProductCreateSerializer,
        responses={201: ProductSerializer, 400: {'description': 'Bad request'}},
        tags=['Products'],
        summary='Create product',
        description='Create a new product (suppliers only)'
    )
    def create(self, request, *args, **kwargs):
        """Create a new product (suppliers only)"""
        # Check if user is a supplier
        if request.user.role not in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT]:
            return Response(
                {"error": "Only suppliers can create products"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        
        response_serializer = ProductSerializer(product, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        request=ProductUpdateSerializer,
        responses={200: ProductSerializer, 400: {'description': 'Bad request'}},
        tags=['Products'],
        summary='Update product',
        description='Update product information (suppliers and admins only)'
    )
    def update(self, request, *args, **kwargs):
        """Update product (suppliers and admins only)"""
        product = self.get_object()
        
        # Check permissions
        if (request.user.role not in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT, UserTypes.ADMIN] or
            (request.user.role in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT] and 
             product.supplier != request.user)):
            return Response(
                {"error": "You can only update your own products"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        responses={204: {'description': 'Product deleted successfully'}},
        tags=['Products'],
        summary='Delete product',
        description='Soft delete a product (suppliers and admins only)'
    )
    def destroy(self, request, *args, **kwargs):
        """Soft delete product (suppliers and admins only)"""
        product = self.get_object()
        
        # Check permissions
        if (request.user.role not in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT, UserTypes.ADMIN] or
            (request.user.role in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT] and 
             product.supplier != request.user)):
            return Response(
                {"error": "You can only delete your own products"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        product.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='query', description='Search query', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='category', description='Filter by category', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='min_price', description='Minimum price', required=False, type=OpenApiTypes.DECIMAL),
            OpenApiParameter(name='max_price', description='Maximum price', required=False, type=OpenApiTypes.DECIMAL),
            OpenApiParameter(name='supplier', description='Filter by supplier', required=False, type=OpenApiTypes.STR),
        ],
        responses={200: ProductListSerializer(many=True)},
        tags=['Products'],
        summary='Search products',
        description='Search and filter products with advanced options'
    )
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """Search products with advanced filtering"""
        query = request.query_params.get('query', '')
        category = request.query_params.get('category', '')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        supplier = request.query_params.get('supplier', '')
        
        queryset = self.get_queryset()
        
        # Text search
        if query:
            queryset = queryset.filter(
                Q(name_en__icontains=query) |
                Q(name_ar__icontains=query) |
                Q(description_en__icontains=query) |
                Q(description_ar__icontains=query)
            )
        
        # Apply filters
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        if supplier:
            queryset = queryset.filter(supplier__username__icontains=supplier)
        
        # Price filtering (role-based)
        user = request.user
        if user.is_authenticated:
            if user.role == UserTypes.B2C_VISITOR:
                price_field = 'end_user_price'
            elif user.role == UserTypes.CORPORATE:
                price_field = 'retail_price_corporate'
            elif user.role == UserTypes.HORECA:
                price_field = 'retail_price_horeca'
            elif user.role in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT]:
                price_field = 'wholesale_price'
            else:
                price_field = 'end_user_price'
        else:
            price_field = 'end_user_price'
        
        if min_price:
            queryset = queryset.filter(**{f"{price_field}__gte": min_price})
        if max_price:
            queryset = queryset.filter(**{f"{price_field}__lte": max_price})
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: ProductListSerializer(many=True)},
        tags=['Products'],
        summary='Get products by category',
        description='Get all products in a specific category'
    )
    @action(detail=False, methods=['get'], url_path='category/(?P<category_name>[^/.]+)')
    def by_category(self, request, category_name=None):
        """Get products by category"""
        queryset = self.get_queryset().filter(category__icontains=category_name)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        responses={200: ProductListSerializer(many=True)},
        tags=['Products'],
        summary='Get products by supplier',
        description='Get all products from a specific supplier'
    )
    @action(detail=False, methods=['get'], url_path='supplier/(?P<supplier_username>[^/.]+)')
    def by_supplier(self, request, supplier_username=None):
        """Get products by supplier username"""
        try:
            supplier = User.objects.get(username=supplier_username)
            queryset = self.get_queryset().filter(supplier=supplier)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ProductListSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            
            serializer = ProductListSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(
        responses={200: {'description': 'Product restored successfully'}},
        tags=['Products'],
        summary='Restore product',
        description='Restore a soft-deleted product (admins only)'
    )
    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        """Restore a soft-deleted product (admins only)"""
        if request.user.role != UserTypes.ADMIN:
            return Response(
                {"error": "Only admins can restore products"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        product = self.get_object()
        if not product.is_deleted:
            return Response(
                {"error": "Product is not deleted"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product.restore()
        return Response({"message": "Product restored successfully"})


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for product categories (read-only)"""
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        responses={200: ProductCategorySerializer(many=True)},
        tags=['Product Categories'],
        summary='List categories',
        description='Get all active product categories'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        responses={200: ProductCategorySerializer},
        tags=['Product Categories'],
        summary='Get category details',
        description='Get detailed information about a specific category'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ProductImageViewSet(viewsets.ModelViewSet):
    """ViewSet for product images (suppliers and admins only)"""
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    
    def get_permissions(self):
        """Only suppliers and admins can manage images"""
        if self.request.user.role not in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT, UserTypes.ADMIN]:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Set the product owner"""
        product_id = self.request.data.get('product')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                if (self.request.user.role in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT] and 
                    product.supplier != self.request.user):
                    raise permissions.PermissionDenied("You can only add images to your own products")
            except Product.DoesNotExist:
                raise permissions.PermissionDenied("Product not found")
        
        serializer.save()
