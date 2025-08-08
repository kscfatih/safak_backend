from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Child

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['phone_number', 'first_name', 'last_name', 'is_phone_verified', 'has_children', 'children_count', 'is_active']
    list_filter = ['is_phone_verified', 'has_children', 'is_active', 'date_joined']
    search_fields = ['phone_number', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name')}),
        ('Çocuk Bilgileri', {'fields': ('has_children', 'children_count')}),
        ('İzinler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'password1', 'password2', 'has_children', 'children_count'),
        }),
    )

class ChildAdmin(admin.ModelAdmin):
    model = Child
    list_display = ['name', 'user', 'grade', 'created_at']
    list_filter = ['grade', 'created_at']
    search_fields = ['name', 'user__first_name', 'user__last_name', 'user__phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'name', 'grade')}),
        ('Tarih Bilgileri', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Child, ChildAdmin)
