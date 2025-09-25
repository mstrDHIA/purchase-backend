from rest_framework import serializers
from .models import PurchaseRequest
from custom_user.serializers import UserSerializer  # Import your user serializer
from django.contrib.auth import get_user_model

User = get_user_model()

class PurchaseRequestSerializer(serializers.ModelSerializer):
    requested_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    approved_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = PurchaseRequest
        fields = '__all__'