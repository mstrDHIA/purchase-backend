from django.shortcuts import render
from rest_framework import viewsets, permissions

from department.models import Department
from department.serializer import DepartmentSerializer

# Create your views here.
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

