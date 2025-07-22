from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchaseRequestViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'purchaseRequests', PurchaseRequestViewSet, basename='purchaseRequest')

urlpatterns = [
    path('', include(router.urls)),
    
]