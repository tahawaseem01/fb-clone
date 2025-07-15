from .models import Notification, Message

def notification_counts(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).exclude(type='message').count(),

            'message_notifications_count': Message.objects.filter(
                recipient=request.user,
                is_read=False,
            ).count()
        }
    return {}
