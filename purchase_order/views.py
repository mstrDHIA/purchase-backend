from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import PurchaseOrder
from .serializers import PurchaseOrderSerializer
from rest_framework.response import Response


# Create your views here.


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PurchaseOrder.objects.all()
        requested_by_id = self.request.query_params.get('requested_by')
        if requested_by_id:
            queryset = queryset.filter(requested_by_id=requested_by_id)
        return queryset




