from rest_framework import serializers
from .models import PurchaseOrder
from custom_user.serializers import UserSerializer  # Import your user serializer

class PurchaseOrderSerializer(serializers.ModelSerializer):
    requested_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'