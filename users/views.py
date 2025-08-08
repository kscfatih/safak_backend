import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, PhoneVerificationSerializer, ChildUpdateSerializer
)
from .models import CustomUser, Child

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    logger.info(f"🔔 Register isteği alındı: {request.data}")
    
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        logger.info("✅ Register validasyonu başarılı")
        user = serializer.save()
        logger.info(f"✅ Kullanıcı oluşturuldu: {user.phone_number}")
        
        # JWT token oluştur
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Kullanıcı başarıyla oluşturuldu.',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    
    logger.error(f"❌ Register validasyonu başarısız: {serializer.errors}")
    return Response({
        'message': 'Kayıt işlemi başarısız.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    logger.info(f"🔔 Login isteği alındı: {request.data}")
    
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']
        
        logger.info(f"🔍 Kullanıcı doğrulanıyor: {phone_number}")
        user = authenticate(phone_number=phone_number, password=password)
        
        if user:
            logger.info(f"✅ Login başarılı: {user.phone_number}")
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Giriş başarılı.',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"❌ Login başarısız: {phone_number}")
            return Response({
                'message': 'Telefon numarası veya şifre hatalı.'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    logger.error(f"❌ Login validasyonu başarısız: {serializer.errors}")
    return Response({
        'message': 'Giriş işlemi başarısız.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_phone(request):
    serializer = PhoneVerificationSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        verification_code = serializer.validated_data['verification_code']
        
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
            
            # Simülasyon için basit doğrulama
            if verification_code == "123456":
                user.is_phone_verified = True
                user.save()
                
                return Response({
                    'message': 'Telefon numarası başarıyla doğrulandı.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Geçersiz doğrulama kodu.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except CustomUser.DoesNotExist:
            return Response({
                'message': 'Kullanıcı bulunamadı.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'message': 'Doğrulama işlemi başarısız.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profil başarıyla güncellendi.',
            'user': UserProfileSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Profil güncellenirken hata oluştu.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user
    user.delete()
    return Response({
        'message': 'Hesap başarıyla silindi.'
    }, status=status.HTTP_200_OK)

# Çocuk bilgileri için yeni endpoint'ler
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_children(request):
    children = request.user.children.all()
    serializer = ChildUpdateSerializer(children, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_child(request):
    serializer = ChildUpdateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({
            'message': 'Çocuk bilgisi başarıyla eklendi.',
            'child': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'message': 'Çocuk bilgisi eklenirken hata oluştu.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_child(request, child_id):
    try:
        child = request.user.children.get(id=child_id)
    except Child.DoesNotExist:
        return Response({
            'message': 'Çocuk bulunamadı.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ChildUpdateSerializer(child, data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Çocuk bilgisi başarıyla güncellendi.',
            'child': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'Çocuk bilgisi güncellenirken hata oluştu.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_child(request, child_id):
    try:
        child = request.user.children.get(id=child_id)
        child.delete()
        return Response({
            'message': 'Çocuk bilgisi başarıyla silindi.'
        }, status=status.HTTP_200_OK)
    except Child.DoesNotExist:
        return Response({
            'message': 'Çocuk bulunamadı.'
        }, status=status.HTTP_404_NOT_FOUND)
