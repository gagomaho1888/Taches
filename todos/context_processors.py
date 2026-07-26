def unread_notification_count(request):
    if request.user.is_authenticated:
        try:
            from .models import Notification
            count = Notification.objects.filter(user=request.user, is_read=False).count()
            return {"unread_notification_count": count}
        except Exception:
            return {"unread_notification_count": 0}
    return {}
