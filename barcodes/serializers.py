from rest_framework import serializers
from .models import Campaign, CampaignBarcode, UserBarcode

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ('id', 'campaign_code', 'campaign_name', 'description', 'is_active', 'start_date', 'end_date')

class CampaignBarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignBarcode
        fields = ('id', 'barcode_code', 'barcode_name', 'campaign_code', 'is_assigned', 'created_at')

class UserBarcodeSerializer(serializers.ModelSerializer):
    barcode_code = serializers.CharField(source='campaign_barcode.barcode_code', read_only=True)
    barcode_name = serializers.CharField(source='campaign_barcode.barcode_name', read_only=True)
    campaign_code = serializers.CharField(source='campaign_barcode.campaign_code', read_only=True)
    campaign_info = serializers.SerializerMethodField()
    
    class Meta:
        model = UserBarcode
        fields = (
            'id', 'barcode_code', 'barcode_name', 'campaign_code', 
            'campaign_info', 'assigned_at'
        )
    
    def get_campaign_info(self, obj):
        try:
            campaign = Campaign.objects.get(campaign_code=obj.campaign_barcode.campaign_code)
            return {
                'name': campaign.campaign_name,
                'description': campaign.description,
                'is_active': campaign.is_active
            }
        except Campaign.DoesNotExist:
            return None