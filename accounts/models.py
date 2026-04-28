from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_b2b_seller = models.BooleanField(default=False) # True if they can sell products
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"

# --- SIGNALS ---
# Bulletproof Signal: Automatically creates/saves a UserProfile whenever a User is created or updated.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # get_or_create safely fetches the profile, or creates it if it's missing 
    # (like for Admins created via the terminal)
    UserProfile.objects.get_or_create(user=instance)