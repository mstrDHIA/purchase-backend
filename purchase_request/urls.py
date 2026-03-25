from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchaseRequestViewSet


router = DefaultRouter()
router.register(r'purchaseRequests', PurchaseRequestViewSet, basename='purchaseRequest')

urlpatterns = [
    path('', include(router.urls)),
]