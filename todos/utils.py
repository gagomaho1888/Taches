from django.utils import timezone


def get_effective_status(tache):
    if tache.status == "done":
        return "done"
    if tache.status == "cancelled":
        return "cancelled"
    if tache.deadline and tache.deadline < timezone.now():
        return "overdue"
    return "progress"


def get_effective_status_label(status):
    labels = {
        "progress": "En cours",
        "done": "Terminé",
        "cancelled": "Annulée",
        "overdue": "En retard",
    }
    return labels.get(status, status)
