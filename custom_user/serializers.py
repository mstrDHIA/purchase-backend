# from django.contrib.auth.models import User
from custom_user.models import User
from rest_framework import serializers

from custom_profile.serializers import ProfileSerializer
from role.serializers import RoleSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ['id', 'username', 'email']
        fields = '__all__'
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user
    

class UserWithDetailsSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(source='profile_id', read_only=True)
    role = RoleSerializer(source='role_id',read_only=True)  # Adjust field name if needed

    class Meta:
        model = User

        fields = '__all__'


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError("New password cannot be the same as the old password.")
        return attrs