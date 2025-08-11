from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import os
from django.core.files.base import ContentFile

User = get_user_model()

class CampaignBarcode(models.Model):
    """Kampanya barkodları - her kampanya için mevcut barkodlar"""
    barcode_code = models.CharField(max_length=6, unique=True, verbose_name='Barkod Kodu')
    barcode_name = models.CharField(max_length=100, verbose_name='Barkod İsmi')
    campaign_code = models.CharField(max_length=50, verbose_name='Kampanya Kodu')
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True, verbose_name='Barkod Görüntüsü')
    is_assigned = models.BooleanField(default=False, verbose_name='Atanmış mı?')
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Kampanya Barkodu'
        verbose_name_plural = 'Kampanya Barkodları'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campaign_code', 'is_active']),
            models.Index(fields=['is_assigned']),
        ]

    def __str__(self):
        return f"{self.barcode_code} - {self.barcode_name} ({self.campaign_code})"

    def save(self, *args, **kwargs):
        # Artık görüntü oluşturmuyoruz - React Native'de dinamik üretilecek
        super().save(*args, **kwargs)


class Campaign(models.Model):
    """Kampanya yönetimi"""
    campaign_code = models.CharField(max_length=50, unique=True, verbose_name='Kampanya Kodu')
    campaign_name = models.CharField(max_length=200, verbose_name='Kampanya Adı')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    start_date = models.DateTimeField(verbose_name='Başlangıç Tarihi')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='Bitiş Tarihi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    class Meta:
        verbose_name = 'Kampanya'
        verbose_name_plural = 'Kampanyalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.campaign_name} ({self.campaign_code})"

    @classmethod
    def get_active_campaign(cls):
        """Aktif kampanyayı getir"""
        from django.utils import timezone
        now = timezone.now()
        return cls.objects.filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
        ).first()


class UserBarcode(models.Model):
    """Kullanıcıya atanan barkodlar"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_barcode', verbose_name='Kullanıcı')
    campaign_barcode = models.OneToOneField(CampaignBarcode, on_delete=models.CASCADE, related_name='assigned_user', verbose_name='Kampanya Barkodu')
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='Atanma Tarihi')

    class Meta:
        verbose_name = 'Kullanıcı Barkodu'
        verbose_name_plural = 'Kullanıcı Barkodları'
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.user.phone_number} - {self.campaign_barcode.barcode_code}"

    @classmethod
    def assign_barcode_to_user(cls, user):
        """Kullanıcıya barkod ata"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Zaten barkodu varsa atama
        if hasattr(user, 'user_barcode'):
            logger.info(f"ASSIGN: Kullanıcının zaten barkodu var: {user.phone_number}")
            return user.user_barcode

        # Aktif kampanyayı bul
        active_campaign = Campaign.get_active_campaign()
        logger.info(f"ASSIGN: Aktif kampanya: {active_campaign.campaign_code if active_campaign else 'YOK'}")
        
        if not active_campaign:
            logger.warning(f"ASSIGN: Aktif kampanya bulunamadı")
            return None

        # Tüm kampanyaları listele (debug için)
        all_campaigns = Campaign.objects.all()
        logger.info(f"ASSIGN: Tüm kampanyalar: {[c.campaign_code for c in all_campaigns]}")
        
        # Aktif kampanyadan atanmamış bir barkod bul
        available_barcode = CampaignBarcode.objects.filter(
            campaign_code=active_campaign.campaign_code,
            is_assigned=False,
            is_active=True
        ).first()
        
        # Debug: Bu kampanya kodunda kaç barkod var?
        total_barcodes = CampaignBarcode.objects.filter(campaign_code=active_campaign.campaign_code).count()
        available_count = CampaignBarcode.objects.filter(
            campaign_code=active_campaign.campaign_code,
            is_assigned=False,
            is_active=True
        ).count()
        
        logger.info(f"ASSIGN: Kampanya {active_campaign.campaign_code} - Toplam: {total_barcodes}, Müsait: {available_count}")

        if not available_barcode:
            logger.warning(f"ASSIGN: Müsait barkod bulunamadı - Kampanya: {active_campaign.campaign_code}")
            return None

        # Barkodu kullanıcıya ata
        available_barcode.is_assigned = True
        available_barcode.save()

        user_barcode = cls.objects.create(
            user=user,
            campaign_barcode=available_barcode
        )
        
        logger.info(f"ASSIGN: Barkod atandı: {user.phone_number} -> {available_barcode.barcode_code}")
        return user_barcode