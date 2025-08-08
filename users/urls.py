from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('verify/', views.verify_phone, name='verify_phone'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    
    # Çocuk bilgileri endpoint'leri
    path('children/', views.get_children, name='get_children'),
    path('children/add/', views.add_child, name='add_child'),
    path('children/<int:child_id>/update/', views.update_child, name='update_child'),
    path('children/<int:child_id>/delete/', views.delete_child, name='delete_child'),
] 