from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddProfileView, ProfileViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('add-profile/', AddProfileView.as_view(), name='add-profile'),
]