from django.urls import path
from . import views

app_name = 'barcodes'

urlpatterns = [
    path('test/', views.test_view, name='test_view'),  # Test için
    path('user-barcode/', views.get_user_barcode, name='get_user_barcode'),
    path('active-campaign/', views.get_active_campaign, name='get_active_campaign'),
    path('assign-barcode/', views.assign_barcode_manual, name='assign_barcode_manual'),
]