from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChangePasswordView, UserViewSet, RegisterView, UserListWithDetailsView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users-with-details/', UserListWithDetailsView.as_view(), name='users-with-details'),
    path('users-with-details/<int:pk>/', UserListWithDetailsView.as_view(), name='users-with-details'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]