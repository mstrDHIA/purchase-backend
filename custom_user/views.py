# from django.contrib.auth.models import User
from custom_user.models import User
from django.shortcuts import render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import ChangePasswordSerializer, RegisterSerializer,CustomTokenObtainPairSerializer, UserSerializer, UserWithDetailsSerializer, UserProfileRoleUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data, status=status.HTTP_201_CREATED
        )


class UserListWithDetailsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        if pk is not None:
            users = User.objects.filter(id=pk)
            if not users.exists():
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            users = User.objects.all()
        serializer = UserWithDetailsSerializer(users, many=True)
        return Response(serializer.data)

# Create your views here.


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserProfileRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Create and assign profile if missing and profile data is provided
        profile_data = request.data.get('profile')
        if profile_data and not user.profile_id:
            from custom_profile.models import Profile
            profile = Profile.objects.create(**profile_data)
            user.profile_id = profile
            user.save()

        # Create and assign role if missing and role data is provided
        print('getting role')
        role_id = request.data.get('role_id')
        print('role: ', role_id)
        if role_id :
            print('aaa')
            from role.models import Role
            try:
                print('bbb')
                role = Role.objects.get(pk=role_id)
                user.role_id = role
                user.save()
            except Role.DoesNotExist:
                return Response({'error': 'Role not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileRoleUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            if not user.is_active:
                return Response({'detail': 'User is not authorized.'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
