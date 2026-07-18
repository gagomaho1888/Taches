from django.utils import timezone
from .models import Tache


def update_task_statuses(user):
    now = timezone.now()

    # Avant deadline → À faire
    Tache.objects.filter(
        user=user,
        deadline__isnull=False,
        deadline__gte=now,
        completed_at__isnull=True,
    ).exclude(status="done").update(status="todo")

    # Après deadline → Terminé
    Tache.objects.filter(
        user=user,
        deadline__isnull=False,
        deadline__lt=now,
        completed_at__isnull=True,
    ).exclude(status="done").update(status="done", completed_at=now)

    # Sans deadline mais start_date passée → Terminé
    Tache.objects.filter(
        user=user,
        deadline__isnull=True,
        start_date__isnull=False,
        start_date__lte=now,
        status="todo",
        completed_at__isnull=True,
    ).update(status="done", completed_at=now)
