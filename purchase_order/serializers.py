from rest_framework import serializers
from .models import PurchaseOrder
from custom_user.serializers import UserSerializer  # Import your user serializer

class PurchaseOrderSerializer(serializers.ModelSerializer):
    # Nested serializers for read operations only
    requested_by_user_detail = UserSerializer(source='requested_by_user', read_only=True)
    approved_by_user_detail = UserSerializer(source='approved_by_user', read_only=True)
    
    # Department convenient access (read-only)
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    requester_username = serializers.CharField(source='requested_by_user.username', read_only=True, allow_null=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'start_date', 'end_date', 'status',
            'approved_by_user', 'products', 'title', 'description',
            'requested_by_user', 'department', 'rejected_reason', 'currency',
            'created_at', 'updated_at', 'priority', 'refuse_reason',
            'purchase_request', 'is_archived', 'supplier_delivery_date',
            'requested_by_user_detail', 'approved_by_user_detail',
            'department_name', 'requester_username'
        ]
        read_only_fields = ['id', 'po_number', 'created_at', 'updated_at', 'requested_by_user_detail', 'approved_by_user_detail', 'department_name', 'requester_username']