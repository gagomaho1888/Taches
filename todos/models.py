import re
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import secrets


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, default="")
    icon = models.CharField(max_length=50, blank=True, default="")
    couleur = models.CharField(max_length=20, default="#000000")

    def __str__(self):
        return self.nom

    def clean(self):
        if self.couleur and not re.match(r'^#[0-9A-Fa-f]{6}$', self.couleur):
            raise ValidationError({"couleur": "La couleur doit être au format hexadécimal (#RRGGBB)."})


class Groupe(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="groupes_diriges"
    )
    code = models.CharField(max_length=12, unique=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = secrets.token_hex(6).upper()
        super().save(*args, **kwargs)


class MembreGroupe(models.Model):
    ROLE_CHOICES = (
        ("leader", "Leader"),
        ("member", "Membre"),
    )

    groupe = models.ForeignKey(
        Groupe,
        on_delete=models.CASCADE,
        related_name="membres"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="membre_groupes"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="member"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("groupe", "user")
        verbose_name = "Membre du groupe"
        verbose_name_plural = "Membres du groupe"

    def __str__(self):
        return f"{self.user.username} - {self.groupe.nom} ({self.get_role_display()})"


class Tache(models.Model):

    PRIORITY = (
        ("low", "Basse"),
        ("medium", "Moyenne"),
        ("high", "Haute"),
        ("urgent", "Urgente"),
    )

    STATUS = (
        ("progress", "En cours"),
        ("done", "Terminé"),
        ("cancelled", "Annulée"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="taches"
    )

    groupe = models.ForeignKey(
        Groupe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="taches"
    )

    title = models.CharField(max_length=200)

    description = models.TextField(
        blank=True,
        null=True
    )

    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY,
        default="medium"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="progress"
    )

    start_date = models.DateTimeField(
        null=True,
        blank=True
    )

    deadline = models.DateTimeField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title

    @property
    def effective_status(self):
        if self.status == "done":
            return "done"
        if self.status == "cancelled":
            return "cancelled"
        if self.deadline and self.deadline < timezone.now():
            return "overdue"
        return "progress"

    @property
    def effective_status_display(self):
        labels = {
            "progress": "En cours",
            "done": "Terminé",
            "cancelled": "Annulée",
            "overdue": "En retard",
        }
        return labels.get(self.effective_status, self.effective_status)


class SousTache(models.Model):

    tache = models.ForeignKey(
        Tache,
        on_delete=models.CASCADE,
        related_name="sous_taches"
    )

    title = models.CharField(max_length=200)

    completed = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.title


class Comment(models.Model):

    tache = models.ForeignKey(
        'Tache',
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Comment by {self.user} on {self.tache}"


class Attachment(models.Model):

    tache = models.ForeignKey(
        'Tache',
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(
        upload_to="attachments/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Attachment for {self.tache}"


class Notification(models.Model):

    TYPE_CHOICES = (
        ("task_assigned", "Tâche assignée"),
        ("task_completed", "Tâche terminée"),
        ("task_updated", "Tâche modifiée"),
        ("task_deleted", "Tâche supprimée"),
        ("comment", "Nouveau commentaire"),
        ("reminder", "Rappel"),
        ("deadline", "Date limite proche"),
        ("overdue", "Tâche en retard"),
        ("system", "Notification système"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    task = models.ForeignKey(
        "Tache",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    title = models.CharField(max_length=150)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    read_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user} - {self.title}"
