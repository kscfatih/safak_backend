from rest_framework import serializers
from .models import OpportunityProduct

class OpportunityProductSerializer(serializers.ModelSerializer):
    discount_percentage = serializers.ReadOnlyField()
    savings_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = OpportunityProduct
        fields = [
            'id', 'name', 'description', 'original_price', 'discounted_price',
            'image', 'is_active', 'created_at', 'discount_percentage', 'savings_amount'
        ]
        read_only_fields = ['id', 'created_at', 'discount_percentage', 'savings_amount'] 