from django.urls import path
from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("taches/", views.tache_list, name="tache_list"),
    path("taches/creer/", views.tache_create, name="tache_create"),
    path("taches/<int:pk>/", views.tache_detail, name="tache_detail"),
    path("taches/<int:pk>/modifier/", views.tache_edit, name="tache_edit"),
    path("taches/<int:pk>/supprimer/", views.tache_delete, name="tache_delete"),
    path("notifications/", views.notifications_list, name="notifications"),
    path("notifications/<int:pk>/lire/", views.notification_mark_read, name="notification_mark_read"),
    path("notifications/tout-lire/", views.notification_mark_all_read, name="notification_mark_all_read"),
    path("notifications/<int:pk>/supprimer/", views.notification_delete, name="notification_delete"),
    path("groupes/", views.groupe_list, name="groupe_list"),
    path("groupes/creer/", views.groupe_create, name="groupe_create"),
    path("groupes/rejoindre/", views.groupe_join, name="groupe_join"),
    path("groupes/<int:pk>/", views.groupe_detail, name="groupe_detail"),
    path("groupes/<int:pk>/supprimer/", views.groupe_delete, name="groupe_delete"),
    path("groupes/<int:pk>/quitter/", views.groupe_leave, name="groupe_leave"),
    path("groupes/<int:pk>/retirer/<int:member_pk>/", views.groupe_remove_member, name="groupe_remove_member"),
    path("groupes/<int:pk>/assigner/", views.groupe_assign_task, name="groupe_assign_task"),
    path("taches/<int:pk>/toggle-status/", views.tache_toggle_status, name="tache_toggle_status"),
    path("categories/creer/", views.categorie_create, name="categorie_create"),
]
