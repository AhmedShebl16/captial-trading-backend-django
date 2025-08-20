from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from users.models import UserTypes

User = get_user_model()


class Product(models.Model):
    """
    Product model with 4 different price types for different user roles
    """
    # Basic product information
    name_en = models.CharField(max_length=200, help_text="Product name in English")
    name_ar = models.CharField(max_length=200, help_text="Product name in Arabic")
    image = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Product image")
    
    # Product details
    description_en = models.TextField(blank=True, null=True, help_text="Product description in English")
    description_ar = models.TextField(blank=True, null=True, help_text="Product description in Arabic")
    
    # Category and classification
    category = models.CharField(max_length=100, blank=True, null=True, help_text="Product category")
    subcategory = models.CharField(max_length=100, blank=True, null=True, help_text="Product subcategory")
    
    # Unit information
    unit = models.CharField(max_length=50, default="KG", help_text="Unit of measurement (KG, Package, etc.)")
    unit_size = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1.0,
        help_text="Size of the unit (e.g., 1.0 for 1 KG, 20.0 for 20 KG package)"
    )
    
    # Price fields for different user types
    # 1. End user price (AI-generated retail market price)
    end_user_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="End user price - retail market price (e.g., 150 L.E for 1 KG)"
    )
    
    # 2. Retail price for B2C (Business to customer wholesale)
    retail_price_b2c = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Retail price for B2C wholesale (e.g., 2000 L.E for 20 KG package)"
    )
    
    # 3. Retail price for Corporates/Purchasing managers
    retail_price_corporate = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Retail price for corporates/purchasing managers (e.g., 1850 L.E for 20 KG package)"
    )
    
    # 4. Retail price for HoReCa
    retail_price_horeca = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Retail price for HoReCa businesses (e.g., 1900 L.E for 20 KG package)"
    )
    
    # 5. Wholesale price for purchasing managers (bulk orders)
    wholesale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Wholesale price for bulk orders (e.g., 1800 L.E for 20 KG package, min 5 packages)"
    )
    wholesale_min_quantity = models.PositiveIntegerField(
        default=5,
        help_text="Minimum quantity required for wholesale price"
    )
    
    # Stock and availability
    stock_quantity = models.PositiveIntegerField(default=0, help_text="Available stock quantity")
    is_available = models.BooleanField(default=True, help_text="Product availability status")
    
    # Supplier information
    supplier = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role__in': [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT]},
        help_text="Product supplier"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'product'
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['supplier', 'is_available']),
            models.Index(fields=['is_deleted']),
        ]
    
    def __str__(self):
        return f"{self.name_en} ({self.name_ar})"
    
    def get_price_for_user(self, user):
        """
        Get the appropriate price for a specific user based on their role
        """
        if not user or not user.is_authenticated:
            return self.end_user_price
        
        if user.role == UserTypes.ADMIN:
            # Admins can see all prices
            return {
                'end_user_price': self.end_user_price,
                'retail_price_b2c': self.retail_price_b2c,
                'retail_price_corporate': self.retail_price_corporate,
                'retail_price_horeca': self.retail_price_horeca,
                'wholesale_price': self.wholesale_price,
                'wholesale_min_quantity': self.wholesale_min_quantity
            }
        
        elif user.role == UserTypes.B2C_VISITOR:
            return self.end_user_price
        
        elif user.role == UserTypes.CORPORATE:
            return self.retail_price_corporate
        
        elif user.role == UserTypes.HORECA:
            return self.retail_price_horeca
        
        elif user.role == UserTypes.SUPPLIER:
            return self.wholesale_price
        
        elif user.role == UserTypes.SUPPLIER_MERCHANT:
            return self.wholesale_price
        
        elif user.role == UserTypes.STORAGE_CLIENT:
            return self.retail_price_corporate
        
        else:
            return self.end_user_price
    
    def get_price_display_for_user(self, user):
        """
        Get formatted price display for a specific user
        """
        price = self.get_price_for_user(user)
        
        if isinstance(price, dict):
            # Admin user - return all prices
            return {
                'end_user_price': f"{self.end_user_price} L.E per {self.unit_size} {self.unit}",
                'retail_price_b2c': f"{self.retail_price_b2c} L.E per {self.unit_size} {self.unit}",
                'retail_price_corporate': f"{self.retail_price_corporate} L.E per {self.unit_size} {self.unit}",
                'retail_price_horeca': f"{self.retail_price_horeca} L.E per {self.unit_size} {self.unit}",
                'wholesale_price': f"{self.wholesale_price} L.E per {self.unit_size} {self.unit} (min {self.wholesale_min_quantity})"
            }
        else:
            # Regular user - return single price
            return f"{price} L.E per {self.unit_size} {self.unit}"
    
    def is_wholesale_eligible(self, user, quantity):
        """
        Check if user is eligible for wholesale price
        """
        if user.role in [UserTypes.SUPPLIER, UserTypes.SUPPLIER_MERCHANT, UserTypes.CORPORATE]:
            return quantity >= self.wholesale_min_quantity
        return False
    
    def soft_delete(self):
        """Soft delete the product"""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_available = False
        self.save(update_fields=['is_deleted', 'deleted_at', 'is_available'])
    
    def restore(self):
        """Restore a soft-deleted product"""
        self.is_deleted = False
        self.deleted_at = None
        self.is_available = True
        self.save(update_fields=['is_deleted', 'deleted_at', 'is_available'])
    
    @property
    def price_per_unit(self):
        """Calculate price per unit (e.g., price per 1 KG)"""
        if self.unit_size > 0:
            return self.end_user_price / self.unit_size
        return self.end_user_price


class ProductCategory(models.Model):
    """
    Product category model for better organization
    """
    name_en = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_category'
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = ['name_en']
    
    def __str__(self):
        return self.name_en
    
    @property
    def has_children(self):
        return self.children.exists()


class ProductImage(models.Model):
    """
    Additional product images
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/additional/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_image'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name_en}"
