from .models import Supplier
from rest_framework import serializers


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class SupplierRecommendationSerializer(SupplierSerializer):
    total_spend = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    orders_count = serializers.IntegerField(read_only=True)
    score = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Supplier
        fields = '__all__'