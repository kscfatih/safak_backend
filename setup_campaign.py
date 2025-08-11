#!/usr/bin/env python
"""
Kampanya kurulum scripti
"""
import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safak_backend.settings')
django.setup()

from barcodes.models import Campaign
from django.utils import timezone
from datetime import timedelta

def setup_campaign():
    """KAMPANYA2025'i oluştur"""
    print("🚀 KAMPANYA2025 kurulumu başlıyor...")
    
    # Kampanyayı oluştur veya güncelle
    campaign, created = Campaign.objects.get_or_create(
        campaign_code='KAMPANYA2025',
        defaults={
            'campaign_name': 'Yeni Yıl 2025 Kampanyası',
            'description': 'Yeni yıl özel indirimleri için barkod kampanyası',
            'is_active': True,
            'start_date': timezone.now(),
            'end_date': None  # Sınırsız
        }
    )
    
    if created:
        print("✅ KAMPANYA2025 kampanyası oluşturuldu!")
    else:
        # Mevcut kampanyayı aktif yap
        campaign.is_active = True
        campaign.start_date = timezone.now()
        campaign.end_date = None
        campaign.save()
        print("✅ KAMPANYA2025 kampanyası güncellendi!")
    
    print(f"📊 Kampanya Bilgileri:")
    print(f"   - Kod: {campaign.campaign_code}")
    print(f"   - Ad: {campaign.campaign_name}")
    print(f"   - Aktif: {campaign.is_active}")
    print(f"   - Başlangıç: {campaign.start_date}")
    print(f"   - Bitiş: {campaign.end_date or 'Sınırsız'}")
    
    # Aktif kampanya kontrolü
    active_campaign = Campaign.get_active_campaign()
    if active_campaign:
        print(f"✅ Aktif kampanya: {active_campaign.campaign_code}")
    else:
        print("❌ Aktif kampanya bulunamadı!")
    
    return campaign

if __name__ == "__main__":
    setup_campaign()