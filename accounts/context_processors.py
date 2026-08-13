# accounts/context_processors.py (Create this file)
from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
        return {
            'unread_notifications': unread_notifications,
            'unread_notif_count': unread_notifications.count()
        }
    return {}