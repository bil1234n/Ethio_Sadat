from django.db import models
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class SocialMediaPost(models.Model):
    """
    Admin-managed social media post. Replaces the old hardcoded
    Instagram / Facebook / TikTok lists with real, editable records
    that can be created, edited, and deleted from the mobile admin app.
    """

    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('tiktok', 'TikTok'),
        ('telegram', 'Telegram'),
    ]

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='facebook')
    link = models.URLField(max_length=500)
    image = models.ImageField(upload_to='social_media_posts/', null=True, blank=True)
    caption = models.TextField(blank=True)
    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        label = self.caption[:40] if self.caption else self.link
        return f"{self.get_platform_display()} - {label}"


# --- CACHE INVALIDATION ---
# The public social feed endpoints (web + mobile) are cached for 30 minutes.
# Whenever an admin adds, edits, or deletes a post we must flush those
# caches immediately so the change is reflected right away instead of
# waiting for the cache to expire.
SOCIAL_FEED_CACHE_KEYS = [
    'bilyonarc_social_feeds_v19',  # socialMedia/views.py (web template)
    'rn_social_feeds_api_v6',      # api/views.py (mobile app API)
]


@receiver([post_save, post_delete], sender=SocialMediaPost)
def clear_social_feed_cache(sender, **kwargs):
    for key in SOCIAL_FEED_CACHE_KEYS:
        cache.delete(key)
