from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'username', 'first_name', 'last_name', 'role', 'created_at', 'is_active', 'is_staff', 'is_superuser', 'is_deleted', 'deleted_at')
    search_fields = ('username', 'first_name', 'last_name', 'user_id')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'is_deleted')
    readonly_fields = ('created_at', 'user_id', 'id', 'deleted_at')
    
    def get_queryset(self, request):
        """Show all users including soft-deleted ones in admin"""
        return User.objects.all_with_deleted()
