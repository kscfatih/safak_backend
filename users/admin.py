from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Child

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('phone_number', 'first_name', 'last_name', 'is_phone_verified', 'has_children', 'children_count', 'is_staff')
    list_filter = ('is_phone_verified', 'has_children', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('phone_number',)
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name')}),
        ('Çocuk Bilgileri', {'fields': ('has_children', 'children_count')}),
        ('Doğrulama', {'fields': ('is_phone_verified',)}),
        ('İzinler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('user', 'grade', 'get_grade_display', 'created_at')
    list_filter = ('grade', 'created_at')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)
    
    def get_grade_display(self, obj):
        return obj.get_grade_display()
    get_grade_display.short_description = 'Sınıf'

admin.site.register(CustomUser, CustomUserAdmin)