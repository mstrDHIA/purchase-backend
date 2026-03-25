from rest_framework import serializers
from .models import PurchaseOrder
from custom_user.serializers import UserSerializer  # Import your user serializer

class PurchaseOrderSerializer(serializers.ModelSerializer):
    requested_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)

    # convenience fields so clients can always see department/requester info
    department = serializers.SerializerMethodField()
    department_id = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    requester_id = serializers.SerializerMethodField()
    requester_username = serializers.SerializerMethodField()

    def get_department(self, obj):
        # return a small dict containing whichever bits we can resolve
        dep_id = self.get_department_id(obj)
        dep_name = self.get_department_name(obj)
        if dep_id is None and not dep_name:
            return None
        res = {}
        if dep_id is not None:
            res['id'] = dep_id
        if dep_name:
            res['name'] = dep_name
        return res

    def get_department_id(self, obj):
        if obj.department_id:
            return obj.department_id
        try:
            pr = getattr(obj, 'purchase_request', None)
            if pr and pr.requested_by and pr.requested_by.dep_id:
                return pr.requested_by.dep_id.id
        except Exception:
            pass
        try:
            usr = getattr(obj, 'requested_by_user', None)
            if usr and usr.dep_id:
                return usr.dep_id.id
        except Exception:
            pass
        return None

    def get_department_name(self, obj):
        if obj.department_id and obj.department:
            try:
                return obj.department.name
            except Exception:
                return str(obj.department)
        try:
            pr = getattr(obj, 'purchase_request', None)
            if pr and pr.requested_by and pr.requested_by.dep_id:
                return pr.requested_by.dep_id.name
        except Exception:
            pass
        try:
            usr = getattr(obj, 'requested_by_user', None)
            if usr and usr.dep_id:
                return usr.dep_id.name
        except Exception:
            pass
        return None

    def get_requester_id(self, obj):
        if obj.requested_by_user_id:
            return obj.requested_by_user_id
        try:
            pr = getattr(obj, 'purchase_request', None)
            if pr and pr.requested_by_id:
                return pr.requested_by_id
        except Exception:
            pass
        return None

    def get_requester_username(self, obj):
        # prefer explicit relation on the PO
        if obj.requested_by_user and hasattr(obj.requested_by_user, 'username'):
            return obj.requested_by_user.username
        # fall back to purchase_request creator if available
        try:
            pr = getattr(obj, 'purchase_request', None)
            if pr and pr.requested_by and hasattr(pr.requested_by, 'username'):
                return pr.requested_by.username
        except Exception:
            pass
        return None

    class Meta:
        model = PurchaseOrder
        fields = '__all__'