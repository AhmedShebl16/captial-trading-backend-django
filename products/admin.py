from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Product, ProductCategory, ProductImage

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name_en', 'name_ar')
    ordering = ('name_en',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'alt_text', 'is_primary', 'order')
    list_filter = ('is_primary', 'product__category')
    search_fields = ('product__name_en', 'product__name_ar')
    ordering = ('product', 'order')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Image Preview'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name_en', 'name_ar', 'category', 'unit_display', 
        'end_user_price', 'stock_quantity', 'is_available', 'supplier_info', 'created_at'
    )
    list_filter = (
        'category', 'is_available', 'is_deleted', 'supplier__role', 'created_at'
    )
    search_fields = ('name_en', 'name_ar', 'supplier__username', 'supplier__company_name')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    
    # Group fields by category
    fieldsets = (
        ('Basic Information', {
            'fields': ('name_en', 'name_ar', 'image', 'description_en', 'description_ar')
        }),
        ('Classification', {
            'fields': ('category', 'subcategory', 'unit', 'unit_size')
        }),
        ('Pricing', {
            'fields': (
                'end_user_price', 'retail_price_b2c', 'retail_price_corporate',
                'retail_price_horeca', 'wholesale_price', 'wholesale_min_quantity'
            ),
            'classes': ('collapse',)
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'is_available')
        }),
        ('Supplier Information', {
            'fields': ('supplier',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Add actions
    actions = ['make_available', 'make_unavailable', 'restore_products']
    
    def unit_display(self, obj):
        """Display unit with size"""
        return f"{obj.unit_size} {obj.unit}"
    unit_display.short_description = 'Unit'
    
    def supplier_info(self, obj):
        """Display supplier information"""
        if obj.supplier:
            role_display = obj.supplier.get_role_display()
            company = obj.supplier.company_name or obj.supplier.username
            return format_html(
                '<span style="color: #007cba;">{}</span><br><small>{}</small>',
                company, role_display
            )
        return "No Supplier"
    supplier_info.short_description = 'Supplier'
    
    def make_available(self, request, queryset):
        """Make selected products available"""
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} products were successfully made available.')
    make_available.short_description = "Make selected products available"
    
    def make_unavailable(self, request, queryset):
        """Make selected products unavailable"""
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} products were successfully made unavailable.')
    make_unavailable.short_description = "Make selected products unavailable"
    
    def restore_products(self, request, queryset):
        """Restore soft-deleted products"""
        restored = 0
        for product in queryset.filter(is_deleted=True):
            product.restore()
            restored += 1
        self.message_user(request, f'{restored} products were successfully restored.')
    restore_products.short_description = "Restore selected products"
    
    def get_queryset(self, request):
        """Show all products including soft-deleted ones in admin"""
        return Product.objects.all()
    
    def get_list_display(self, request):
        """Customize list display based on user permissions"""
        if request.user.is_superuser:
            return self.list_display
        # For non-superusers, show fewer fields
        return ('name_en', 'name_ar', 'category', 'unit_display', 'end_user_price', 'is_available')
