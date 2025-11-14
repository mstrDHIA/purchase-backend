from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Category
from .serializers import CategorySerializer

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Category.objects.all()
        parent_category = self.request.query_params.get('parent_category')
        if parent_category:
            queryset = queryset.filter(parent_category=parent_category)
        return queryset