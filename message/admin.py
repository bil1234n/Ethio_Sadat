from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'is_replied', 'created_at')
    list_filter = ('is_replied', 'created_at')
    search_fields = ('subject', 'user__username', 'message')
    
    # Prevent admin from editing the user's original message
    readonly_fields = ('user', 'subject', 'message', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Message', {
            'fields': ('user', 'subject', 'message', 'created_at')
        }),
        ('Admin Action', {
            'fields': ('admin_reply', 'is_replied')
        }),
    )

    # Automatically set 'is_replied' to True if admin types a reply
    def save_model(self, request, obj, form, change):
        if obj.admin_reply and not obj.is_replied:
            obj.is_replied = True
        super().save_model(request, obj, form, change)