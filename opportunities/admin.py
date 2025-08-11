from django.contrib import admin
from .models import OpportunityProduct

@admin.register(OpportunityProduct)
class OpportunityProductAdmin(admin.ModelAdmin):
    list_display = ( 'original_price', 'discounted_price', 'discount_percentage', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('description',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('description', 'image')
        }),
        ('Fiyat Bilgileri', {
            'fields': ('original_price', 'discounted_price')
        }),
        ('Durum', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def discount_percentage(self, obj):
        return f"%{obj.discount_percentage}"
    discount_percentage.short_description = 'İndirim %'
