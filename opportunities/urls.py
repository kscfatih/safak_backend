from django.urls import path
from . import views

app_name = 'opportunities'

urlpatterns = [
    path('', views.OpportunityProductListAPIView.as_view(), name='opportunity_list'),
] 