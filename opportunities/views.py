from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import OpportunityProduct
from .serializers import OpportunityProductSerializer

# Create your views here.

class OpportunityProductListAPIView(generics.ListAPIView):
    """Aktif fırsat ürünlerini listele"""
    queryset = OpportunityProduct.objects.filter(is_active=True)
    serializer_class = OpportunityProductSerializer
    permission_classes = [IsAuthenticated]
