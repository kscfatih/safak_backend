from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from barcodes.models import UserBarcode
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def assign_barcode_to_new_user(sender, instance, created, **kwargs):
    """Yeni kullanıcı oluşturulduğunda barkod ata"""
    if created:
        logger.info(f"SIGNAL: Yeni kullanıcı oluşturuldu: {instance.phone_number}")
        try:
            from barcodes.models import Campaign, CampaignBarcode
            
            # Debug bilgileri
            active_campaign = Campaign.get_active_campaign()
            logger.info(f"SIGNAL: Aktif kampanya: {active_campaign.campaign_code if active_campaign else 'YOK'}")
            
            if active_campaign:
                available_count = CampaignBarcode.objects.filter(
                    campaign_code=active_campaign.campaign_code,
                    is_assigned=False,
                    is_active=True
                ).count()
                logger.info(f"SIGNAL: Müsait barkod sayısı: {available_count}")
            
            user_barcode = UserBarcode.assign_barcode_to_user(instance)
            if user_barcode:
                logger.info(f"SIGNAL: Kullanıcıya barkod atandı: {instance.phone_number} -> {user_barcode.campaign_barcode.barcode_code}")
            else:
                logger.warning(f"SIGNAL: Kullanıcıya barkod atanamadı (aktif kampanya veya müsait barkod yok): {instance.phone_number}")
        except Exception as e:
            logger.error(f"SIGNAL: Barkod atama hatası: {instance.phone_number} - {str(e)}")
            import traceback
            logger.error(f"SIGNAL: Traceback: {traceback.format_exc()}")