from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RejectReasonViewSet


router = DefaultRouter()
router.register(r'rejectReasons', RejectReasonViewSet, basename='rejectReasons')

urlpatterns = [
    path('', include(router.urls)),
]