from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
import json

from users.models import CustomUser, Child
from users.serializers import UserRegistrationSerializer
from opportunities.models import OpportunityProduct
from barcodes.models import UserBarcode, Campaign


def home_view(request):
    """Ana sayfa - Barkod gösterimi"""
    if not request.user.is_authenticated:
        return redirect('webapp:login')
    
    # Kullanıcının barkodunu al
    user_barcode = None
    try:
        user_barcode = UserBarcode.objects.select_related('campaign_barcode').get(user=request.user)
    except UserBarcode.DoesNotExist:
        # Barkod yoksa otomatik ata
        user_barcode = UserBarcode.assign_barcode_to_user(request.user)
    
    # Aktif kampanya bilgisi
    active_campaign = None
    try:
        active_campaign = Campaign.objects.filter(is_active=True).first()
    except Campaign.DoesNotExist:
        pass
    
    context = {
        'user': request.user,
        'user_barcode': user_barcode,
        'active_campaign': active_campaign,
    }
    return render(request, 'web/home.html', context)


def login_view(request):
    """Giriş sayfası"""
    if request.user.is_authenticated:
        return redirect('webapp:home')
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        if phone_number and password:
            user = authenticate(request, username=phone_number, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Başarıyla giriş yaptınız!')
                return redirect('webapp:home')
            else:
                messages.error(request, 'Telefon numarası veya şifre hatalı!')
        else:
            messages.error(request, 'Tüm alanları doldurun!')
    
    return render(request, 'web/login.html')


def register_view(request):
    """Kayıt sayfası"""
    if request.user.is_authenticated:
        return redirect('webapp:home')
    
    if request.method == 'POST':
        try:
            # Form verilerini al
            data = {
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'phone_number': request.POST.get('phone_number'),
                'password': request.POST.get('password'),
                'password_confirm': request.POST.get('password_confirm'),
                'has_children': request.POST.get('has_children') == 'on',
                'children_count': int(request.POST.get('children_count', 0)),
                'children': []
            }
            
            # Çocuk bilgilerini al
            if data['has_children'] and data['children_count'] > 0:
                for i in range(data['children_count']):
                    grade = request.POST.get(f'child_{i}_grade')
                    if grade:
                        data['children'].append({'grade': grade})
            
            # Serializer ile kayıt
            serializer = UserRegistrationSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                login(request, user)
                messages.success(request, 'Başarıyla kayıt oldunuz!')
                return redirect('webapp:home')
            else:
                # Hataları göster
                for field, errors in serializer.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                        
        except Exception as e:
            messages.error(request, f'Kayıt sırasında hata oluştu: {str(e)}')
    
    return render(request, 'web/register.html')


@login_required
def opportunities_view(request):
    """Fırsat ürünleri sayfası"""
    products = OpportunityProduct.objects.filter(is_active=True).order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(products, 6)  # Sayfa başına 6 ürün
    page_number = request.GET.get('page')
    page_products = paginator.get_page(page_number)
    
    context = {
        'products': page_products,
        'user': request.user,
    }
    return render(request, 'web/opportunities.html', context)


@login_required
def profile_view(request):
    """Profil sayfası"""
    context = {
        'user': request.user,
        'children': Child.objects.filter(user=request.user),
    }
    return render(request, 'web/profile.html', context)


def logout_view(request):
    """Çıkış"""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız!')
    return redirect('webapp:login')


@csrf_exempt
def get_children_count(request):
    """AJAX - Çocuk sayısı değiştiğinde form alanlarını güncelle"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            children_count = int(data.get('children_count', 0))
            
            # HTML form alanları oluştur
            html = ""
            for i in range(children_count):
                html += f'''
                <div class="child-input">
                    <label for="child_{i}_grade">Çocuk {i+1} Sınıfı:</label>
                    <select name="child_{i}_grade" id="child_{i}_grade" required>
                        <option value="">Sınıf Seçin</option>
                        <option value="3_yas">3 Yaş</option>
                        <option value="4_yas">4 Yaş</option>
                        <option value="5_yas">5 Yaş</option>
                        <option value="1_sinif">1. Sınıf</option>
                        <option value="2_sinif">2. Sınıf</option>
                        <option value="3_sinif">3. Sınıf</option>
                        <option value="4_sinif">4. Sınıf</option>
                        <option value="5_sinif">5. Sınıf</option>
                        <option value="6_sinif">6. Sınıf</option>
                        <option value="7_sinif">7. Sınıf</option>
                        <option value="8_sinif">8. Sınıf</option>
                        <option value="9_sinif">9. Sınıf</option>
                        <option value="10_sinif">10. Sınıf</option>
                        <option value="11_sinif">11. Sınıf</option>
                        <option value="12_sinif">12. Sınıf</option>
                    </select>
                </div>
                '''
            
            return JsonResponse({'html': html})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def privacy_policy_view(request):
    """Gizlilik Politikası sayfası"""
    context = {
        'current_date': timezone.now(),
    }
    return render(request, 'web/privacy-policy.html', context)