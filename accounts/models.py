from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.db.models.signals import pre_save # Add pre_save import
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_b2b_seller = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"

# --- BULLETPROOF SIGNALS & NORMALIZATION ---

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Safely handles profile generation and forces lowercase emails"""
    # Normalize the email string to lowercase whenever a standard user updates
    if instance.email and not instance.email.islower():
        User.objects.filter(pk=instance.pk).update(email=instance.email.lower())

    UserProfile.objects.get_or_create(user=instance)

# --- ENFORCE STRICT DATABASE UNIQUENESS BEFORE SAVING ---
@receiver(pre_save, sender=User)
def check_unique_email(sender, instance, **kwargs):
    """Prevents saving a user if their email matches another account case-insensitively"""
    if instance.email:
        instance.email = instance.email.lower() # Force lowercase storage

        # Look for any OTHER user with the exact same email
        duplicate_exists = User.objects.filter(email__iexact=instance.email).exclude(pk=instance.pk).exists()
        if duplicate_exists:
            raise ValidationError(f"Database Integrity Violation: The email '{instance.email}' is already registered.")

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('Product', 'Product'),
        ('Order', 'Order'),
        ('Status', 'Status'),
        ('Message', 'Message'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='Order')
    link = models.CharField(max_length=255, blank=True, null=True) # Where to redirect on click
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"


class SiteSettings(models.Model):
    """
    Single-row table for app-wide settings that the admin can edit from the
    mobile app instead of hardcoding them in source code. Currently just
    holds the Telegram username that "Order on Telegram" buttons message.
    """
    telegram_order_username = models.CharField(
        max_length=100,
        default='Ahamuti',
        help_text="Telegram username that receives product orders. Do not include the @ symbol.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1  # Enforce a single settings row
        if self.telegram_order_username:
            # Be forgiving if someone types "@Ahamuti" instead of "Ahamuti"
            self.telegram_order_username = self.telegram_order_username.strip().lstrip('@')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # The singleton row should never be deleted

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'telegram_order_username': 'Ahamuti'})
        return obj

    def __str__(self):
        return "Site Settings"
