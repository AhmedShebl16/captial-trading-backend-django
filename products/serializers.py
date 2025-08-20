from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, ProductCategory, ProductImage
from users.models import UserTypes

User = get_user_model()


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories"""
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'name_en', 'name_ar', 'description', 'parent', 'is_active']


class ProductSerializer(serializers.ModelSerializer):
    """Base product serializer with role-based price display"""
    
    # Include related fields
    supplier_username = serializers.CharField(source='supplier.username', read_only=True)
    supplier_company = serializers.CharField(source='supplier.company_name', read_only=True)
    additional_images = ProductImageSerializer(many=True, read_only=True)
    
    # Price fields (will be filtered based on user role)
    price_for_user = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    is_wholesale_eligible = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_en', 'name_ar', 'image', 'description_en', 'description_ar',
            'category', 'subcategory', 'unit', 'unit_size', 'stock_quantity', 'is_available',
            'supplier', 'supplier_username', 'supplier_company',
            'additional_images', 'price_for_user', 'price_display', 'is_wholesale_eligible',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'supplier_username', 'supplier_company']
    
    def get_price_for_user(self, obj):
        """Get price based on user role"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.get_price_for_user(request.user)
        return obj.end_user_price
    
    def get_price_display(self, obj):
        """Get formatted price display based on user role"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.get_price_display_for_user(request.user)
        return f"{obj.end_user_price} L.E per {obj.unit_size} {obj.unit}"
    
    def get_is_wholesale_eligible(self, obj):
        """Check if user is eligible for wholesale pricing"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Default to False, will be calculated based on quantity in order context
            return False
        return False


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products (suppliers only)"""
    
    class Meta:
        model = Product
        fields = [
            'name_en', 'name_ar', 'image', 'description_en', 'description_ar',
            'category', 'subcategory', 'unit', 'unit_size', 'end_user_price',
            'retail_price_b2c', 'retail_price_corporate', 'retail_price_horeca',
            'wholesale_price', 'wholesale_min_quantity', 'stock_quantity'
        ]
    
    def validate(self, attrs):
        """Validate that the user is a supplier and prices are logical"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.role not in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT]:
                raise serializers.ValidationError("Only suppliers can create products")
            
            # Validate price logic (wholesale should be lower than retail)
            wholesale_price = attrs.get('wholesale_price', 0)
            retail_prices = [
                attrs.get('retail_price_b2c', 0),
                attrs.get('retail_price_corporate', 0),
                attrs.get('retail_price_horeca', 0)
            ]
            
            if wholesale_price > min(retail_prices):
                raise serializers.ValidationError("Wholesale price should be lower than retail prices")
        
        return attrs
    
    def create(self, validated_data):
        """Set the supplier to the current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['supplier'] = request.user
        return super().create(validated_data)


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating products"""
    
    class Meta:
        model = Product
        fields = [
            'name_en', 'name_ar', 'image', 'description_en', 'description_ar',
            'category', 'subcategory', 'unit', 'unit_size', 'end_user_price',
            'retail_price_b2c', 'retail_price_corporate', 'retail_price_horeca',
            'wholesale_price', 'wholesale_min_quantity', 'stock_quantity', 'is_available'
        ]
    
    def validate(self, attrs):
        """Validate price logic"""
        # Get current instance values for comparison
        instance = self.instance
        if instance:
            wholesale_price = attrs.get('wholesale_price', instance.wholesale_price)
            retail_prices = [
                attrs.get('retail_price_b2c', instance.retail_price_b2c),
                attrs.get('retail_price_corporate', instance.retail_price_corporate),
                attrs.get('retail_price_horeca', instance.retail_price_horeca)
            ]
            
            if wholesale_price > min(retail_prices):
                raise serializers.ValidationError("Wholesale price should be lower than retail prices")
        
        return attrs


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product lists"""
    
    price_for_user = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    supplier_name = serializers.CharField(source='supplier.username', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_en', 'name_ar', 'image', 'category', 'unit', 'unit_size',
            'stock_quantity', 'is_available', 'supplier_name', 'price_for_user',
            'price_display', 'created_at'
        ]
    
    def get_price_for_user(self, obj):
        """Get price based on user role"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.get_price_for_user(request.user)
        return obj.end_user_price
    
    def get_price_display(self, obj):
        """Get formatted price display based on user role"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.get_price_display_for_user(request.user)
        return f"{obj.end_user_price} L.E per {obj.unit_size} {obj.unit}"


class ProductDetailSerializer(ProductSerializer):
    """Detailed product serializer with all information"""
    
    # Include all price fields for admin users
    all_prices = serializers.SerializerMethodField()
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['all_prices']
    
    def get_all_prices(self, obj):
        """Get all prices (for admin users)"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == UserTypes.ADMIN:
            return {
                'end_user_price': obj.end_user_price,
                'retail_price_b2c': obj.retail_price_b2c,
                'retail_price_corporate': obj.retail_price_corporate,
                'retail_price_horeca': obj.retail_price_horeca,
                'wholesale_price': obj.wholesale_price,
                'wholesale_min_quantity': obj.wholesale_min_quantity
            }
        return None


class ProductSearchSerializer(serializers.Serializer):
    """Serializer for product search parameters"""
    query = serializers.CharField(required=False, help_text="Search query for product name")
    category = serializers.CharField(required=False, help_text="Filter by category")
    min_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, help_text="Minimum price filter")
    max_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, help_text="Maximum price filter")
    supplier = serializers.CharField(required=False, help_text="Filter by supplier username")
    available_only = serializers.BooleanField(default=True, help_text="Show only available products")
    page = serializers.IntegerField(default=1, min_value=1, help_text="Page number")
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100, help_text="Items per page")
