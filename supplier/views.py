from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Supplier
from .serializers import SupplierSerializer

# Create your views here.

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]