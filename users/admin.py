from django.contrib import admin
from django.utils.html import format_html
from .models import User, UserTypes

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_id', 'username', 'first_name', 'last_name', 
        'role_display', 'company_name', 'business_type', 'phone_number',
        'is_active', 'is_staff', 'is_superuser', 'is_verified', 'is_deleted'
    )
    search_fields = ('username', 'first_name', 'last_name', 'user_id', 'email', 'company_name')
    list_filter = (
        'role', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'is_deleted',
        'created_at'
    )
    readonly_fields = ('created_at', 'user_id', 'id', 'deleted_at')
    
    # Group fields by category
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password')
        }),
        ('User Type & Role', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified')
        }),
        ('Business Information', {
            'fields': ('company_name', 'business_type', 'phone_number', 'address'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'user_id', 'id'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Add actions
    actions = ['activate_users', 'deactivate_users', 'verify_users', 'unverify_users']
    
    def role_display(self, obj):
        """Display role with color coding"""
        role_colors = {
            UserTypes.ADMIN: '#FF0000',  # Red for admin
            UserTypes.B2C_VISITOR: '#007BFF',  # Blue for visitor
            UserTypes.CORPORATE: '#28A745',  # Green for corporate
            UserTypes.HORECA: '#FFC107',  # Yellow for HoReCa
            UserTypes.SUPPLIER: '#17A2B8',  # Cyan for supplier
            UserTypes.SUPPLIER_MERCHANT: '#6F42C1',  # Purple for supplier merchant
            UserTypes.STORAGE_CLIENT: '#FD7E14',  # Orange for storage client
        }
        
        color = role_colors.get(obj.role, '#6C757D')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_display.short_description = 'Role'
    
    def get_queryset(self, request):
        """Show all users including soft-deleted ones in admin"""
        return User.objects.all_with_deleted()
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were successfully activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were successfully deactivated.')
    deactivate_users.short_description = "Deactivate selected users"
    
    def verify_users(self, request, queryset):
        """Verify selected users"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} users were successfully verified.')
    verify_users.short_description = "Verify selected users"
    
    def unverify_users(self, request, queryset):
        """Unverify selected users"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} users were successfully unverified.')
    unverify_users.short_description = "Unverify selected users"
    
    def get_list_display(self, request):
        """Customize list display based on user permissions"""
        if request.user.is_superuser:
            return self.list_display
        # For non-superusers, show fewer fields
        return ('username', 'first_name', 'last_name', 'role_display', 'is_active', 'is_verified')
