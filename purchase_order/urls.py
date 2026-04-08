from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchaseOrderViewSet, PurchaseOrderLineViewSet
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

router = DefaultRouter()
router.register(r'purchaseOrders', PurchaseOrderViewSet, basename='purchaseOrder')
router.register(r'lines', PurchaseOrderLineViewSet, basename='purchaseOrderLine')

urlpatterns = [
    path('', include(router.urls)),
]