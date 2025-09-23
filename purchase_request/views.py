from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import PurchaseRequest
from .serializers import PurchaseRequestSerializer
from rest_framework.response import Response


# Create your views here.


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PurchaseRequest.objects.all()
        requested_by_id = self.request.query_params.get('requested_by')
        if requested_by_id:
            queryset = queryset.filter(requested_by_id=requested_by_id)
        return queryset




