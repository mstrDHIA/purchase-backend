from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import PurchaseRequest
from .serializers import PurchaseRequestSerializer

# Create your views here.

class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
