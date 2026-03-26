from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import User

@receiver(user_logged_in)
def update_last_seen_on_login(sender, request, user, **kwargs):
    user.is_online = True
    user.last_seen = timezone.now()
    user.save(update_fields=['is_online', 'last_seen'])

@receiver(user_logged_out)
def update_last_seen_on_logout(sender, request, user, **kwargs):
    user.is_online = False
    user.save(update_fields=['is_online'])