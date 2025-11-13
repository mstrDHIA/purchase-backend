from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

router = DefaultRouter()
router.register(r'category', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]