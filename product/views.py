from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Product.objects.all()
        subcategory = self.request.query_params.get('subcategory')
        if subcategory:
            queryset = queryset.filter(subcategory=subcategory)
        return queryset
