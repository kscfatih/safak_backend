from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import UserBarcode, Campaign
from .serializers import UserBarcodeSerializer, CampaignSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_view(request):
    """Test endpoint - barcodes app'inin çalışıp çalışmadığını kontrol et"""
    from .models import CampaignBarcode
    
    # Kampanya ve barkod durumunu kontrol et
    active_campaign = Campaign.get_active_campaign()
    total_barcodes = CampaignBarcode.objects.count()
    available_barcodes = CampaignBarcode.objects.filter(is_assigned=False, is_active=True).count()
    
    return Response({
        'success': True,
        'message': 'Barcodes app çalışıyor!',
        'app': 'barcodes',
        'debug_info': {
            'active_campaign': active_campaign.campaign_code if active_campaign else None,
            'total_barcodes': total_barcodes,
            'available_barcodes': available_barcodes,
            'campaign_count': Campaign.objects.count()
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_barcode(request):
    """Kullanıcının barkodunu getir - yoksa otomatik ata"""
    try:
        # Önce mevcut barkodu kontrol et
        user_barcode = UserBarcode.objects.select_related('campaign_barcode').filter(user=request.user).first()
        
        # Barkod yoksa otomatik ata
        if not user_barcode:
            logger.info(f"Kullanıcıya barkod atanıyor: {request.user.phone_number}")
            user_barcode = UserBarcode.assign_barcode_to_user(request.user)
            
            if not user_barcode:
                logger.warning(f"Kullanıcıya barkod atanamadı - müsait barkod yok: {request.user.phone_number}")
                return Response({
                    'success': False,
                    'message': 'Şu anda atanabilecek bir barkod bulunmamaktadır. Lütfen daha sonra tekrar deneyin.',
                    'barcode': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            logger.info(f"Kullanıcıya barkod otomatik atandı: {request.user.phone_number} -> {user_barcode.campaign_barcode.barcode_code}")
        
        # Barkod bilgilerini döndür
        serializer = UserBarcodeSerializer(user_barcode, context={'request': request})
        
        return Response({
            'success': True,
            'barcode': serializer.data,
            'message': 'Barkod başarıyla alındı.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Kullanıcı barkodu getirme/atama hatası: {request.user.phone_number} - {str(e)}")
        return Response({
            'success': False,
            'message': 'Barkod bilgileri alınırken bir hata oluştu.',
            'barcode': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_campaign(request):
    """Aktif kampanya bilgilerini getir"""
    try:
        active_campaign = Campaign.get_active_campaign()
        
        if active_campaign:
            serializer = CampaignSerializer(active_campaign)
            return Response({
                'success': True,
                'campaign': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Şu anda aktif bir kampanya bulunmamaktadır.',
                'campaign': None
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        logger.error(f"Aktif kampanya getirme hatası: {str(e)}")
        return Response({
            'success': False,
            'message': 'Kampanya bilgileri alınırken bir hata oluştu.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_barcode_manual(request):
    """Kullanıcıya manuel barkod atama (admin için - force assign)"""
    try:
        # Mevcut barkodu kontrol et
        existing_barcode = UserBarcode.objects.filter(user=request.user).first()
        
        if existing_barcode:
            return Response({
                'success': False,
                'message': f'Bu kullanıcıya zaten bir barkod atanmış: {existing_barcode.campaign_barcode.barcode_code}',
                'barcode': UserBarcodeSerializer(existing_barcode, context={'request': request}).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Yeni barkod ata
        user_barcode = UserBarcode.assign_barcode_to_user(request.user)
        
        if user_barcode:
            serializer = UserBarcodeSerializer(user_barcode, context={'request': request})
            logger.info(f"Manuel barkod atama başarılı: {request.user.phone_number} -> {user_barcode.campaign_barcode.barcode_code}")
            return Response({
                'success': True,
                'message': 'Barkod başarıyla atandı.',
                'barcode': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Şu anda atanabilecek bir barkod bulunmamaktadır.'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        logger.error(f"Manuel barkod atama hatası: {request.user.phone_number} - {str(e)}")
        return Response({
            'success': False,
            'message': 'Barkod atanırken bir hata oluştu.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)