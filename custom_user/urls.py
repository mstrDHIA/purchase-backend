from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChangePasswordView,CustomTokenObtainPairView, UpdateUserProfileRoleView, UserViewSet, RegisterView, UserListWithDetailsView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users-with-details-list/', UserListWithDetailsView.as_view(), name='users-with-details-list'),
    path('users-with-details/<int:pk>/', UserListWithDetailsView.as_view(), name='users-with-details'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/update-all/<int:pk>/', UpdateUserProfileRoleView.as_view(), name='update-user-profile-role'),
]