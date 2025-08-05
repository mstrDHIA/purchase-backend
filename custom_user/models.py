from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    
    # Add custom fields here
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_id = models.OneToOneField(
        'custom_profile.Profile',on_delete=models.CASCADE,
        related_name='user_profile', blank=True, null=True)
    role_id = models.OneToOneField(
        'role.Role',on_delete=models.CASCADE,
        related_name='role', blank=True, null=True)
    
    # Add more fields as needed

    def __str__(self):
        return self.username
