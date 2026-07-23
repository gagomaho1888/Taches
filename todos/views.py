from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import timedelta

from .models import Tache, Categorie, SousTache, Comment, Notification, Groupe, MembreGroupe
from .forms import TacheForm, SousTacheForm, CommentForm, GroupeForm, RejoindreGroupeForm, AssignTacheForm, CategorieForm
from .utils import get_effective_status, get_effective_status_label


@login_required
def accueil(request):
    user = request.user
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    base_qs = Tache.objects.filter(user=user)

    status_stats = base_qs.aggregate(
        total=Count("id"),
        progress=Count("id", filter=Q(status="progress")),
        done=Count("id", filter=Q(status="done")),
        cancelled=Count("id", filter=Q(status="cancelled")),
    )
    overdue_count = base_qs.filter(
        status="progress", deadline__isnull=False, deadline__lt=now
    ).count()
    status_stats["overdue"] = overdue_count

    overdue_tasks = base_qs.filter(
        status="progress", deadline__isnull=False, deadline__lt=now
    )
    for tache in overdue_tasks:
        if not Notification.objects.filter(
            user=user, task=tache, notification_type="overdue"
        ).exists():
            Notification.objects.create(
                user=user,
                task=tache,
                title="Tâche en retard",
                message=f"La tâche « {tache.title} » a dépassé son échéance.",
                notification_type="overdue",
            )
    priority_stats = base_qs.aggregate(
        low=Count("id", filter=Q(priority="low")),
        medium=Count("id", filter=Q(priority="medium")),
        high=Count("id", filter=Q(priority="high")),
        urgent=Count("id", filter=Q(priority="urgent")),
    )

    recent_count = base_qs.filter(created_at__gte=week_ago).count()

    cat_id = request.GET.get("cat", "")
    categories = Categorie.objects.annotate(
        task_count=Count("tache", filter=Q(tache__user=user))
    ).order_by("-task_count")

    taches_categorie = base_qs.all()
    categorie_active = None
    if cat_id:
        categorie_active = get_object_or_404(Categorie, pk=cat_id)
        taches_categorie = taches_categorie.filter(categorie=categorie_active)
    taches_categorie = taches_categorie.order_by("-created_at")[:10]

    upcoming = base_qs.filter(
        deadline__gte=now,
        status="progress"
    ).order_by("deadline")[:5]

    recent_tasks = base_qs.order_by("-updated_at")[:3]

    unread_notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by("-created_at")[:5]

    tasks_with_notifs = set(
        Notification.objects.filter(
            user=user, is_read=False, task__isnull=False
        ).values_list("task_id", flat=True)
    )

    context = {
        **status_stats,
        **priority_stats,
        "recent_count": recent_count,
        "upcoming": upcoming,
        "recent_tasks": recent_tasks,
        "categories": categories,
        "categorie_active": categorie_active,
        "taches_categorie": taches_categorie,
        "unread_notifications": unread_notifications,
        "tasks_with_notifications": tasks_with_notifs,
    }
    return render(request, "accueil.html", context)


@login_required
def tache_list(request):
    user = request.user
    statut = request.GET.get("statut", "")
    priorite = request.GET.get("priorite", "")
    categorie = request.GET.get("categorie", "")
    recherche = request.GET.get("q", "")

    taches = Tache.objects.filter(user=user).select_related("categorie", "groupe")

    if statut:
        taches = taches.filter(status=statut)
    if priorite:
        taches = taches.filter(priority=priorite)
    if categorie:
        taches = taches.filter(categorie_id=categorie)
    if recherche:
        taches = taches.filter(
            Q(title__icontains=recherche) | Q(description__icontains=recherche)
        )

    taches = taches.order_by("-created_at")
    categories = Categorie.objects.all()

    tasks_with_notifs = set(
        Notification.objects.filter(
            user=user, is_read=False, task__isnull=False
        ).values_list("task_id", flat=True)
    )

    paginator = Paginator(taches, 12)
    page = request.GET.get("page")
    taches_page = paginator.get_page(page)

    context = {
        "taches": taches_page,
        "categories": categories,
        "statut_actuel": statut,
        "priorite_actuelle": priorite,
        "categorie_actuelle": categorie,
        "recherche_actuelle": recherche,
        "tasks_with_notifications": tasks_with_notifs,
    }
    return render(request, "tache_list.html", context)


@login_required
def tache_create(request):
    if request.method == "POST":
        form = TacheForm(request.POST)
        if form.is_valid():
            tache = form.save(commit=False)
            tache.user = request.user
            now = timezone.now()
            if tache.status == "done" and not tache.completed_at:
                tache.completed_at = now
            tache.save()
            messages.success(request, "Tâche créée avec succès.")
            return redirect(f"/taches/{tache.pk}/?created=1")
    else:
        form = TacheForm()

    return render(request, "tache_form.html", {
        "form": form,
        "categories": Categorie.objects.all().order_by("nom"),
        "titre_page": "Nouvelle tâche",
        "bouton_texte": "Créer",
    })


@login_required
def tache_detail(request, pk):
    tache = get_object_or_404(Tache, pk=pk)
    if tache.user != request.user:
        if not tache.groupe or not MembreGroupe.objects.filter(
            groupe=tache.groupe, user=request.user
        ).exists():
            from django.http import Http404
            raise Http404
    sous_taches = tache.sous_taches.all()
    comments = tache.comments.order_by("-created_at")

    if request.method == "POST":
        if "add_subtask" in request.POST:
            sub_form = SousTacheForm(request.POST)
            if sub_form.is_valid():
                st = sub_form.save(commit=False)
                st.tache = tache
                st.save()
                return redirect("tache_detail", pk=pk)

        if "toggle_subtask" in request.POST:
            st_id = request.POST.get("subtask_id")
            st = get_object_or_404(SousTache, pk=st_id, tache=tache)
            st.completed = not st.completed
            st.save()
            return redirect("tache_detail", pk=pk)

        if "delete_subtask" in request.POST:
            st_id = request.POST.get("subtask_id")
            st = get_object_or_404(SousTache, pk=st_id, tache=tache)
            st.delete()
            return redirect("tache_detail", pk=pk)

        if "add_comment" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.tache = tache
                comment.user = request.user
                comment.save()

                if tache.user != request.user:
                    Notification.objects.create(
                        user=tache.user,
                        task=tache,
                        title="Nouveau commentaire",
                        message=f"{request.user.username} a commenté sur « {tache.title} ».",
                        notification_type="comment",
                    )

                return redirect("tache_detail", pk=pk)

    sub_form = SousTacheForm()
    comment_form = CommentForm()
    total_sub = sous_taches.count()
    done_sub = sous_taches.filter(completed=True).count()

    return render(request, "tache_detail.html", {
        "tache": tache,
        "sous_taches": sous_taches,
        "comments": comments,
        "sub_form": sub_form,
        "comment_form": comment_form,
        "total_sub": total_sub,
        "done_sub": done_sub,
    })


@login_required
def tache_edit(request, pk):
    tache = get_object_or_404(Tache, pk=pk, user=request.user)

    if request.method == "POST":
        form = TacheForm(request.POST, instance=tache)
        if form.is_valid():
            old_status = tache.status
            tache = form.save()
            if old_status != "done" and tache.status == "done" and not tache.completed_at:
                tache.completed_at = timezone.now()
                tache.save()
            messages.success(request, "Tâche modifiée avec succès.")
            return redirect("tache_detail", pk=tache.pk)
    else:
        form = TacheForm(instance=tache)

    return render(request, "tache_form.html", {
        "form": form,
        "tache": tache,
        "categories": Categorie.objects.all().order_by("nom"),
        "titre_page": "Modifier la tâche",
        "bouton_texte": "Enregistrer",
    })


@login_required
def tache_delete(request, pk):
    tache = get_object_or_404(Tache, pk=pk, user=request.user)

    if request.method == "POST":
        tache.delete()
        messages.success(request, "Tâche supprimée.")
        return redirect("tache_list")

    return render(request, "tache_confirm_delete.html", {"tache": tache})


@login_required
def notifications_list(request):
    notifs = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "notifications.html", {"notifications": notifs})


@login_required
def notification_mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.read_at = timezone.now()
    notif.save()
    return redirect("notifications")


@login_required
def notification_mark_all_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        messages.success(request, "Toutes les notifications ont été marquées comme lues.")
    return redirect("notifications")


@login_required
def notification_delete(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    if request.method == "POST":
        notif.delete()
    return redirect("notifications")


@login_required
def groupe_list(request):
    groupes = Groupe.objects.filter(membres__user=request.user).select_related("leader")
    rejoindre_form = RejoindreGroupeForm()
    return render(request, "groupe_list.html", {
        "groupes": groupes,
        "rejoindre_form": rejoindre_form,
    })


@login_required
def groupe_create(request):
    if request.method == "POST":
        form = GroupeForm(request.POST)
        if form.is_valid():
            groupe = form.save(commit=False)
            groupe.leader = request.user
            groupe.save()
            MembreGroupe.objects.create(
                groupe=groupe,
                user=request.user,
                role="leader"
            )
            messages.success(request, f"Groupe « {groupe.nom} » créé avec succès.")
            return redirect("groupe_detail", pk=groupe.pk)
    else:
        form = GroupeForm()

    return render(request, "groupe_form.html", {
        "form": form,
        "titre_page": "Créer un groupe",
        "bouton_texte": "Créer",
    })


@login_required
def groupe_join(request):
    if request.method == "POST":
        form = RejoindreGroupeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"].upper()
            try:
                groupe = Groupe.objects.get(code=code)
            except Groupe.DoesNotExist:
                messages.error(request, "Code invalide. Groupe introuvable.")
                return redirect("groupe_list")

            if MembreGroupe.objects.filter(groupe=groupe, user=request.user).exists():
                messages.warning(request, "Vous êtes déjà membre de ce groupe.")
            else:
                MembreGroupe.objects.create(
                    groupe=groupe,
                    user=request.user,
                    role="member"
                )
                messages.success(request, f"Vous avez rejoint le groupe « {groupe.nom} ».")
            return redirect("groupe_detail", pk=groupe.pk)
    return redirect("groupe_list")


@login_required
def groupe_delete(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk, leader=request.user)

    if request.method == "POST":
        nom = groupe.nom
        groupe.delete()
        messages.success(request, f"Groupe « {nom} » supprimé.")
        return redirect("groupe_list")

    return render(request, "groupe_confirm_delete.html", {"groupe": groupe})


@login_required
def groupe_leave(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    membre = get_object_or_404(MembreGroupe, groupe=groupe, user=request.user)

    if membre.role == "leader":
        messages.error(request, "Le leader ne peut pas quitter son groupe.")
        return redirect("groupe_detail", pk=pk)

    if request.method == "POST":
        membre.delete()
        messages.success(request, f"Vous avez quitté le groupe « {groupe.nom} ».")
        return redirect("groupe_list")

    return render(request, "groupe_confirm_leave.html", {"groupe": groupe})


@login_required
def groupe_remove_member(request, pk, member_pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    membre = get_object_or_404(MembreGroupe, pk=member_pk, groupe=groupe)

    if request.user != groupe.leader:
        messages.error(request, "Seul le leader peut retirer des membres.")
        return redirect("groupe_detail", pk=pk)

    if membre.user == request.user:
        messages.error(request, "Vous ne pouvez pas vous retirer vous-même.")
        return redirect("groupe_detail", pk=pk)

    if request.method == "POST":
        membre.delete()
        messages.success(request, f"{membre.user.username} a été retiré du groupe.")
        return redirect("groupe_detail", pk=pk)

    return render(request, "groupe_confirm_remove_member.html", {
        "groupe": groupe,
        "membre": membre,
    })


@login_required
def groupe_detail(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    membre = MembreGroupe.objects.filter(groupe=groupe, user=request.user).first()

    if not membre:
        messages.error(request, "Vous n'êtes pas membre de ce groupe.")
        return redirect("groupe_list")

    is_leader = membre.role == "leader"
    membres = groupe.membres.select_related("user").order_by("-role", "joined_at")
    taches = Tache.objects.filter(groupe=groupe).select_related("user", "categorie").order_by("-created_at")

    assign_form = None
    if is_leader:
        assign_form = AssignTacheForm()
        choices = [(m.user.id, m.user.username) for m in membres if m.user.id != request.user.id]
        assign_form.fields["assigned_to"].choices = choices
        assign_form.fields["assigned_to"].widget.choices = choices

    tasks_with_notifs = set(
        Notification.objects.filter(
            user=request.user, is_read=False, task__isnull=False, task__groupe=groupe
        ).values_list("task_id", flat=True)
    )

    return render(request, "groupe_detail.html", {
        "groupe": groupe,
        "membre": membre,
        "is_leader": is_leader,
        "membres": membres,
        "taches": taches,
        "assign_form": assign_form,
        "code": groupe.code,
        "tasks_with_notifications": tasks_with_notifs,
    })


@login_required
def groupe_assign_task(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    membre = MembreGroupe.objects.filter(groupe=groupe, user=request.user).first()

    if not membre or membre.role != "leader":
        messages.error(request, "Seul le leader peut assigner des tâches.")
        return redirect("groupe_list")

    if request.method == "POST":
        form = AssignTacheForm(request.POST)
        membres = groupe.membres.select_related("user").exclude(user=request.user)
        choices = [(m.user.id, m.user.username) for m in membres]
        form.fields["assigned_to"].choices = choices
        form.fields["assigned_to"].widget.choices = choices

        if form.is_valid():
            assigned_user_id = form.cleaned_data["assigned_to"]

            if assigned_user_id == request.user.id:
                messages.error(request, "Vous ne pouvez pas vous assigner de tâche vous-même.")
                return redirect("groupe_detail", pk=pk)

            if not MembreGroupe.objects.filter(groupe=groupe, user_id=assigned_user_id).exists():
                messages.error(request, "Cet utilisateur n'est pas membre du groupe.")
                return redirect("groupe_detail", pk=pk)

            from django.contrib.auth import get_user_model
            User = get_user_model()
            assigned_user = get_object_or_404(User, pk=assigned_user_id)

            tache = Tache.objects.create(
                user=assigned_user,
                groupe=groupe,
                title=form.cleaned_data["title"],
                description=form.cleaned_data.get("description", ""),
                priority=form.cleaned_data["priority"],
                deadline=form.cleaned_data.get("deadline"),
                status="progress",
            )

            Notification.objects.create(
                user=assigned_user,
                task=tache,
                title="Nouvelle tâche assignée",
                message=f"Le leader vous a assigné la tâche « {tache.title} » dans le groupe « {groupe.nom} ».",
                notification_type="task_assigned",
            )

            messages.success(request, f"Tâche assignée à {assigned_user.username}.")
            return redirect("groupe_detail", pk=pk)

    return redirect("groupe_detail", pk=pk)


@login_required
@require_POST
def tache_toggle_status(request, pk):
    tache = get_object_or_404(Tache, pk=pk, user=request.user)
    now = timezone.now()

    if tache.status == "done":
        tache.status = "progress"
        tache.completed_at = None
    else:
        tache.status = "done"
        tache.completed_at = now

    Tache.objects.filter(pk=tache.pk).select_for_update().update(
        status=tache.status, completed_at=tache.completed_at
    )
    tache.refresh_from_db()

    if tache.status == "done" and tache.groupe:
        membres = MembreGroupe.objects.filter(groupe=tache.groupe).exclude(user=request.user).select_related("user")
        for m in membres:
            Notification.objects.create(
                user=m.user,
                task=tache,
                title="Tâche terminée",
                message=f"{request.user.username} a terminé la tâche « {tache.title} ».",
                notification_type="task_completed",
            )

    effective = get_effective_status(tache)

    return JsonResponse({
        "ok": True,
        "new_status": effective,
        "new_label": get_effective_status_label(effective),
        "completed_at": tache.completed_at.strftime("%d/%m/%Y %H:%M") if tache.completed_at else None,
    })


@login_required
def categorie_create(request):
    if request.method == "POST":
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            next_url = request.GET.get("next", "")
            if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                next_url = ""
            target = reverse("tache_create") if not next_url else next_url
            messages.success(request, "Catégorie créée avec succès.")
            return redirect(target)
    else:
        form = CategorieForm()

    return render(request, "categorie_form.html", {"form": form})
