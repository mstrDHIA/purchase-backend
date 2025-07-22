from rest_framework import serializers
from .models import PurchaseRequest

class PurchaseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = '__all__'