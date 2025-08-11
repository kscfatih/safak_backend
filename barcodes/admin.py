from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Campaign, CampaignBarcode, UserBarcode

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('campaign_name', 'campaign_code', 'is_active', 'start_date', 'end_date', 'barcode_count', 'assigned_count')
    list_filter = ('is_active', 'start_date', 'created_at')
    search_fields = ('campaign_name', 'campaign_code', 'description')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('campaign_name', 'campaign_code', 'description')
        }),
        ('Tarihler', {
            'fields': ('start_date', 'end_date')
        }),
        ('Durum', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def barcode_count(self, obj):
        count = CampaignBarcode.objects.filter(campaign_code=obj.campaign_code).count()
        return f"{count} adet"
    barcode_count.short_description = 'Toplam Barkod'
    
    def assigned_count(self, obj):
        count = CampaignBarcode.objects.filter(campaign_code=obj.campaign_code, is_assigned=True).count()
        return f"{count} adet"
    assigned_count.short_description = 'Atanan Barkod'

@admin.register(CampaignBarcode)
class CampaignBarcodeAdmin(admin.ModelAdmin):
    list_display = ('barcode_code', 'barcode_name', 'campaign_code', 'is_assigned', 'is_active', 'barcode_preview', 'created_at')
    list_filter = ('campaign_code', 'is_assigned', 'is_active', 'created_at')
    search_fields = ('barcode_code', 'barcode_name', 'campaign_code')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Barkod Bilgileri', {
            'fields': ('barcode_code', 'barcode_name', 'campaign_code')
        }),
        ('Barkod Görüntüsü', {
            'fields': ('barcode_image', 'barcode_preview_large')
        }),
        ('Durum', {
            'fields': ('is_assigned', 'is_active')
        }),
    )
    
    readonly_fields = ('barcode_preview_large', 'created_at', 'updated_at')
    
    def barcode_preview(self, obj):
        if obj.barcode_image:
            return format_html(
                '<img src="{}" width="80" height="30" style="border: 1px solid #ddd;" />',
                obj.barcode_image.url
            )
        return "Görüntü Yok"
    barcode_preview.short_description = 'Önizleme'
    
    def barcode_preview_large(self, obj):
        if obj.barcode_image:
            return format_html(
                '<img src="{}" width="300" height="100" style="border: 1px solid #ddd;" />',
                obj.barcode_image.url
            )
        return "Görüntü Yok"
    barcode_preview_large.short_description = 'Barkod Görüntüsü'
    
    actions = ['regenerate_barcode_images', 'mark_as_unassigned']
    
    def regenerate_barcode_images(self, request, queryset):
        updated = 0
        for barcode in queryset:
            if barcode.generate_barcode_image():
                barcode.save()
                updated += 1
        
        self.message_user(request, f'{updated} adet barkod görüntüsü yeniden oluşturuldu.')
    regenerate_barcode_images.short_description = 'Seçili barkod görüntülerini yeniden oluştur'
    
    def mark_as_unassigned(self, request, queryset):
        # Sadece atanmamış barkodları işaretleyelim
        unassigned_barcodes = queryset.filter(assigned_user__isnull=True)
        updated = unassigned_barcodes.update(is_assigned=False)
        self.message_user(request, f'{updated} adet barkod atanmamış olarak işaretlendi.')
    mark_as_unassigned.short_description = 'Seçili barkodları atanmamış olarak işaretle'

@admin.register(UserBarcode)
class UserBarcodeAdmin(admin.ModelAdmin):
    list_display = ('user_phone', 'user_name', 'barcode_code', 'campaign_code', 'barcode_preview', 'assigned_at')
    list_filter = ('campaign_barcode__campaign_code', 'assigned_at')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name', 'campaign_barcode__barcode_code')
    ordering = ('-assigned_at',)
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'user_info')
        }),
        ('Barkod Bilgileri', {
            'fields': ('campaign_barcode', 'barcode_info', 'barcode_preview_large')
        }),
    )
    
    readonly_fields = ('user_info', 'barcode_info', 'barcode_preview_large', 'assigned_at')
    
    def user_phone(self, obj):
        return obj.user.phone_number
    user_phone.short_description = 'Telefon'
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_name.short_description = 'Ad Soyad'
    
    def barcode_code(self, obj):
        return obj.campaign_barcode.barcode_code
    barcode_code.short_description = 'Barkod Kodu'
    
    def campaign_code(self, obj):
        return obj.campaign_barcode.campaign_code
    campaign_code.short_description = 'Kampanya'
    
    def barcode_preview(self, obj):
        if obj.campaign_barcode.barcode_image:
            return format_html(
                '<img src="{}" width="80" height="30" style="border: 1px solid #ddd;" />',
                obj.campaign_barcode.barcode_image.url
            )
        return "Görüntü Yok"
    barcode_preview.short_description = 'Önizleme'
    
    def user_info(self, obj):
        return format_html(
            '<strong>Telefon:</strong> {}<br>'
            '<strong>Ad Soyad:</strong> {}<br>'
            '<strong>Kayıt Tarihi:</strong> {}',
            obj.user.phone_number,
            f"{obj.user.first_name} {obj.user.last_name}",
            obj.user.date_joined.strftime('%d.%m.%Y %H:%M')
        )
    user_info.short_description = 'Kullanıcı Detayları'
    
    def barcode_info(self, obj):
        return format_html(
            '<strong>Barkod Kodu:</strong> {}<br>'
            '<strong>Barkod Adı:</strong> {}<br>'
            '<strong>Kampanya:</strong> {}',
            obj.campaign_barcode.barcode_code,
            obj.campaign_barcode.barcode_name,
            obj.campaign_barcode.campaign_code
        )
    barcode_info.short_description = 'Barkod Detayları'
    
    def barcode_preview_large(self, obj):
        if obj.campaign_barcode.barcode_image:
            return format_html(
                '<img src="{}" width="300" height="100" style="border: 1px solid #ddd;" />',
                obj.campaign_barcode.barcode_image.url
            )
        return "Görüntü Yok"
    barcode_preview_large.short_description = 'Barkod Görüntüsü'