from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Tache, Categorie, SousTache, Comment, Notification, Groupe, MembreGroupe
from .utils import update_task_statuses

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@test.com")
        self.assertTrue(self.user.check_password("testpass123"))

    def test_user_str(self):
        self.assertEqual(str(self.user), "testuser")

    def test_default_role(self):
        self.assertEqual(self.user.role, "user")


class CategorieModelTest(TestCase):
    def setUp(self):
        self.cat = Categorie.objects.create(
            nom="Cuisine", description="Tâches culinaires", icon="utensils", couleur="#ff0000"
        )

    def test_categorie_str(self):
        self.assertEqual(str(self.cat), "Cuisine")

    def test_categorie_fields(self):
        self.assertEqual(self.cat.description, "Tâches culinaires")
        self.assertEqual(self.cat.icon, "utensils")
        self.assertEqual(self.cat.couleur, "#ff0000")


class TacheModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )
        self.cat = Categorie.objects.create(nom="Cuisine", icon="utensils")
        self.tache = Tache.objects.create(
            user=self.user,
            title="Cuisiner un oeuf",
            description="Faire un oeuf au plat",
            categorie=self.cat,
            priority="medium",
            status="todo",
        )

    def test_tache_str(self):
        self.assertEqual(str(self.tache), "Cuisiner un oeuf")

    def test_tache_defaults(self):
        self.assertEqual(self.tache.status, "todo")
        self.assertEqual(self.tache.priority, "medium")
        self.assertIsNone(self.tache.completed_at)

    def test_tache_completed_at_on_create(self):
        tache = Tache.objects.create(
            user=self.user, title="Tâche terminée", status="done"
        )
        # completed_at is set by the view, not by the model
        self.assertIsNone(tache.completed_at)

    def test_tache_category_optional(self):
        tache = Tache.objects.create(
            user=self.user, title="Sans catégorie"
        )
        self.assertIsNone(tache.categorie)


class SousTacheModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )
        self.tache = Tache.objects.create(
            user=self.user, title="Tâche test"
        )

    def test_sous_tache_creation(self):
        st = SousTache.objects.create(tache=self.tache, title="Sous-tâche 1")
        self.assertEqual(st.title, "Sous-tâche 1")
        self.assertFalse(st.completed)

    def test_sous_tache_toggle(self):
        st = SousTache.objects.create(tache=self.tache, title="Sous-tâche 1")
        st.completed = True
        st.save()
        st.refresh_from_db()
        self.assertTrue(st.completed)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )
        self.tache = Tache.objects.create(
            user=self.user, title="Tâche test"
        )

    def test_comment_creation(self):
        comment = Comment.objects.create(
            tache=self.tache, user=self.user, content="Bon travail !"
        )
        self.assertEqual(comment.content, "Bon travail !")
        self.assertEqual(comment.user, self.user)


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )

    def test_notification_creation(self):
        notif = Notification.objects.create(
            user=self.user,
            title="Nouvelle tâche",
            message="Une tâche vous a été assignée",
            notification_type="task_assigned",
        )
        self.assertFalse(notif.is_read)
        self.assertIsNone(notif.read_at)


class ViewLoginRequiredTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_accueil_redirect(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_tache_list_redirect(self):
        response = self.client.get("/taches/")
        self.assertEqual(response.status_code, 302)

    def test_tache_create_redirect(self):
        response = self.client.get("/taches/creer/")
        self.assertEqual(response.status_code, 302)

    def test_login_page_accessible(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_register_page_accessible(self):
        response = self.client.get("/inscription/")
        self.assertEqual(response.status_code, 200)


class AuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )

    def test_login_success(self):
        response = self.client.post("/login/", {
            "username": "testuser",
            "password": "testpass123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response.url)

    def test_login_failure(self):
        response = self.client.post("/login/", {
            "username": "testuser",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_register_success(self):
        response = self.client.post("/inscription/", {
            "username": "newuser",
            "email": "new@test.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        })
        self.assertEqual(response.status_code, 302)


class AuthenticatedViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )
        self.client.login(username="testuser", password="testpass123")

    def test_accueil_status(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_tache_list_status(self):
        response = self.client.get("/taches/")
        self.assertEqual(response.status_code, 200)

    def test_tache_create_get(self):
        response = self.client.get("/taches/creer/")
        self.assertEqual(response.status_code, 200)

    def test_tache_create_post(self):
        response = self.client.post("/taches/creer/", {
            "title": "Nouvelle tâche",
            "priority": "medium",
            "status": "todo",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tache.objects.filter(title="Nouvelle tâche").exists())

    def test_tache_detail(self):
        tache = Tache.objects.create(user=self.user, title="Test detail")
        response = self.client.get(f"/taches/{tache.pk}/")
        self.assertEqual(response.status_code, 200)

    def test_tache_detail_other_user(self):
        other = User.objects.create_user(
            username="other", password="pass123", email="o@t.com"
        )
        tache = Tache.objects.create(user=other, title="Pas la mienne")
        response = self.client.get(f"/taches/{tache.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_tache_edit(self):
        tache = Tache.objects.create(user=self.user, title="À modifier")
        response = self.client.post(f"/taches/{tache.pk}/modifier/", {
            "title": "Modifiée",
            "priority": "high",
            "status": "progress",
        })
        self.assertEqual(response.status_code, 302)
        tache.refresh_from_db()
        self.assertEqual(tache.title, "Modifiée")

    def test_tache_delete(self):
        tache = Tache.objects.create(user=self.user, title="À supprimer")
        response = self.client.post(f"/taches/{tache.pk}/supprimer/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tache.objects.filter(pk=tache.pk).exists())

    def test_notifications_page(self):
        response = self.client.get("/notifications/")
        self.assertEqual(response.status_code, 200)

    def test_add_comment(self):
        tache = Tache.objects.create(user=self.user, title="Test")
        response = self.client.post(f"/taches/{tache.pk}/", {
            "add_comment": "1",
            "content": "Mon commentaire",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(content="Mon commentaire").exists())

    def test_add_subtask(self):
        tache = Tache.objects.create(user=self.user, title="Test")
        response = self.client.post(f"/taches/{tache.pk}/", {
            "add_subtask": "1",
            "title": "Sous-tâche",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SousTache.objects.filter(title="Sous-tâche").exists())


class PaginationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )
        self.client.login(username="testuser", password="testpass123")
        for i in range(20):
            Tache.objects.create(user=self.user, title=f"Tâche {i}")

    def test_pagination(self):
        response = self.client.get("/taches/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["taches"]), 12)

    def test_pagination_page_2(self):
        response = self.client.get("/taches/?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["taches"]), 8)


class UpdateTaskStatusesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )

    def test_future_deadline_sets_todo(self):
        tache = Tache.objects.create(
            user=self.user, title="Future",
            deadline=timezone.now() + timedelta(days=5),
            status="progress",
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "todo")

    def test_future_hour_today_sets_todo(self):
        tache = Tache.objects.create(
            user=self.user, title="Plus tard aujourd'hui",
            deadline=timezone.now() + timedelta(hours=6),
            status="progress",
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "todo")

    def test_today_deadline_sets_progress(self):
        tache = Tache.objects.create(
            user=self.user, title="Aujourd'hui",
            deadline=timezone.now(),
            status="todo",
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "progress")

    def test_past_deadline_sets_done(self):
        tache = Tache.objects.create(
            user=self.user, title="Passée",
            deadline=timezone.now() - timedelta(days=3),
            status="todo",
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "done")
        self.assertIsNotNone(tache.completed_at)

    def test_no_deadline_not_changed(self):
        tache = Tache.objects.create(
            user=self.user, title="Pas de deadline", status="progress"
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "progress")

    def test_cancelled_not_changed(self):
        tache = Tache.objects.create(
            user=self.user, title="Annulée",
            deadline=timezone.now() - timedelta(days=1),
            status="cancelled",
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "cancelled")

    def test_other_user_not_affected(self):
        other = User.objects.create_user(
            username="other", password="pass123", email="o@t.com"
        )
        tache = Tache.objects.create(
            user=other, title="Autre",
            deadline=timezone.now() - timedelta(days=1),
            status="todo",
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "todo")

    def test_manual_done_not_overridden(self):
        tache = Tache.objects.create(
            user=self.user, title="Fait manuellement",
            deadline=timezone.now() + timedelta(days=5),
            status="done",
            completed_at=timezone.now(),
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "done")


class IsOverdueTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )

    def test_urgent_past_deadline_is_done(self):
        tache = Tache.objects.create(
            user=self.user, title="Urgente passée",
            priority="urgent",
            deadline=timezone.now() - timedelta(days=1),
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "progress")

    def test_urgent_future_deadline_is_todo(self):
        tache = Tache.objects.create(
            user=self.user, title="Urgente future",
            priority="urgent",
            deadline=timezone.now() + timedelta(days=1),
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "todo")

    def test_high_past_deadline_is_done(self):
        tache = Tache.objects.create(
            user=self.user, title="Haute passée",
            priority="high",
            deadline=timezone.now() - timedelta(days=1),
        )
        update_task_statuses(self.user)
        tache.refresh_from_db()
        self.assertEqual(tache.status, "done")


class GroupeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )
        self.groupe = Groupe.objects.create(
            nom="Dev Team", description="Équipe dev", leader=self.user
        )

    def test_groupe_str(self):
        self.assertEqual(str(self.groupe), "Dev Team")

    def test_groupe_code_unique(self):
        self.assertTrue(len(self.groupe.code) == 8)

    def test_membre_creation(self):
        membre = MembreGroupe.objects.create(
            groupe=self.groupe, user=self.user, role="leader"
        )
        self.assertEqual(membre.role, "leader")

    def test_unique_together(self):
        MembreGroupe.objects.create(groupe=self.groupe, user=self.user, role="leader")
        with self.assertRaises(Exception):
            MembreGroupe.objects.create(groupe=self.groupe, user=self.user, role="member")


class GroupeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )
        self.other = User.objects.create_user(
            username="other", password="pass123", email="o@t.com"
        )
        self.groupe = Groupe.objects.create(
            nom="Dev Team", description="Équipe dev", leader=self.user
        )
        MembreGroupe.objects.create(groupe=self.groupe, user=self.user, role="leader")
        self.client.login(username="testuser", password="testpass123")

    def test_groupe_list_status(self):
        response = self.client.get("/groupes/")
        self.assertEqual(response.status_code, 200)

    def test_groupe_create(self):
        response = self.client.post("/groupes/creer/", {
            "nom": "Nouveau groupe",
            "description": "Description",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Groupe.objects.filter(nom="Nouveau groupe").exists())

    def test_groupe_detail_as_member(self):
        response = self.client.get(f"/groupes/{self.groupe.pk}/")
        self.assertEqual(response.status_code, 200)

    def test_groupe_detail_not_member(self):
        self.client.login(username="other", password="pass123")
        response = self.client.get(f"/groupes/{self.groupe.pk}/")
        self.assertEqual(response.status_code, 302)

    def test_groupe_join(self):
        self.client.login(username="other", password="pass123")
        response = self.client.post("/groupes/rejoindre/", {
            "code": self.groupe.code,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MembreGroupe.objects.filter(
            groupe=self.groupe, user=self.other
        ).exists())

    def test_groupe_join_wrong_code(self):
        self.client.login(username="other", password="pass123")
        response = self.client.post("/groupes/rejoindre/", {
            "code": "WRONGCODE",
        })
        self.assertEqual(response.status_code, 302)

    def test_groupe_leave(self):
        MembreGroupe.objects.create(groupe=self.groupe, user=self.other, role="member")
        self.client.login(username="other", password="pass123")
        response = self.client.post(f"/groupes/{self.groupe.pk}/quitter/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MembreGroupe.objects.filter(
            groupe=self.groupe, user=self.other
        ).exists())

    def test_leader_cannot_leave(self):
        response = self.client.post(f"/groupes/{self.groupe.pk}/quitter/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MembreGroupe.objects.filter(
            groupe=self.groupe, user=self.user
        ).exists())

    def test_groupe_assign_task(self):
        MembreGroupe.objects.create(groupe=self.groupe, user=self.other, role="member")
        response = self.client.post(f"/groupes/{self.groupe.pk}/assigner/", {
            "title": "Tâche assignée",
            "priority": "high",
            "assigned_to": self.other.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tache.objects.filter(
            title="Tâche assignée", user=self.other, groupe=self.groupe
        ).exists())

    def test_assign_sends_notification(self):
        MembreGroupe.objects.create(groupe=self.groupe, user=self.other, role="member")
        self.client.post(f"/groupes/{self.groupe.pk}/assigner/", {
            "title": "Tâche notif",
            "priority": "medium",
            "assigned_to": self.other.pk,
        })
        self.assertTrue(Notification.objects.filter(
            user=self.other, notification_type="task_assigned"
        ).exists())

    def test_non_leader_cannot_assign(self):
        MembreGroupe.objects.create(groupe=self.groupe, user=self.other, role="member")
        self.client.login(username="other", password="pass123")
        response = self.client.post(f"/groupes/{self.groupe.pk}/assigner/", {
            "title": "Tâche refusée",
            "priority": "low",
            "assigned_to": self.user.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tache.objects.filter(title="Tâche refusée").exists())

    def test_assign_to_non_member_rejected(self):
        outsider = User.objects.create_user(
            username="outsider", password="pass123", email="o@x.com"
        )
        response = self.client.post(f"/groupes/{self.groupe.pk}/assigner/", {
            "title": "Tâche extérieur",
            "priority": "low",
            "assigned_to": outsider.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tache.objects.filter(title="Tâche extérieur").exists())

    def test_leader_can_assign_to_self(self):
        response = self.client.post(f"/groupes/{self.groupe.pk}/assigner/", {
            "title": "Tâche pour moi",
            "priority": "high",
            "assigned_to": self.user.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tache.objects.filter(
            title="Tâche pour moi", user=self.user, groupe=self.groupe
        ).exists())

    def test_leader_self_not_in_dropdown(self):
        response = self.client.get(f"/groupes/{self.groupe.pk}/")
        self.assertEqual(response.status_code, 200)
        form_content = response.context["assign_form"].as_p()
        self.assertNotIn(self.user.username, form_content)
