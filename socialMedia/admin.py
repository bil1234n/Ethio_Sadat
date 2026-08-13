from django.contrib import admin
from .models import SocialMediaPost


@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(admin.ModelAdmin):
    list_display = ('platform', 'caption', 'date', 'created_at')
    list_filter = ('platform',)
    search_fields = ('caption', 'link')
    ordering = ('-date', '-created_at')
