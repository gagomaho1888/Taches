from django.contrib import admin
from .models import Tache, Categorie, SousTache, Comment, Notification, Attachment, Groupe, MembreGroupe


@admin.register(Tache)
class TacheAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'status', 'start_date', 'deadline', 'completed_at', 'created_at', 'updated_at')


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'couleur')


@admin.register(SousTache)
class SousTacheAdmin(admin.ModelAdmin):
    list_display = ('title', 'tache', 'completed')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('tache', 'user', 'content', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('tache', 'file', 'uploaded_at')


@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'leader', 'code', 'created_at')


@admin.register(MembreGroupe)
class MembreGroupeAdmin(admin.ModelAdmin):
    list_display = ('groupe', 'user', 'role', 'joined_at')
