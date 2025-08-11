from django.urls import path
from . import views

app_name = 'webapp'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('opportunities/', views.opportunities_view, name='opportunities'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('ajax/children-count/', views.get_children_count, name='children_count'),
]