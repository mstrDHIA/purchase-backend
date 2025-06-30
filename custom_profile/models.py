from django.db import models

# Create your models here.
class Profile(models.Model):
    # user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    # profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)


    def __str__(self):
        return f"{self.user.username}'s Profile"