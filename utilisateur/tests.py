from django.test import TestCase, Client
from django.contrib.auth import get_user_model

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

    def test_optional_fields_blank(self):
        self.assertIsNone(self.user.phone)
        self.assertFalse(self.user.avatar)
        self.assertIsNone(self.user.bio)
        self.assertIsNone(self.user.date_of_birth)
        self.assertIsNone(self.user.location)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )

    def test_login_page_status(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post("/login/", {
            "username": "testuser",
            "password": "testpass123",
        })
        self.assertEqual(response.status_code, 302)

    def test_login_failure(self):
        response = self.client.post("/login/", {
            "username": "testuser",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)

    def test_login_already_authenticated_redirects(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 302)

    def test_login_next_param(self):
        response = self.client.post("/login/?next=/taches/", {
            "username": "testuser",
            "password": "testpass123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("/taches/", response.url)


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_status(self):
        response = self.client.get("/inscription/")
        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        response = self.client.post("/inscription/", {
            "username": "newuser",
            "email": "new@test.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_already_authenticated_redirects(self):
        user = User.objects.create_user(
            username="testuser", password="testpass123", email="t@test.com"
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/inscription/")
        self.assertEqual(response.status_code, 302)

    def test_register_duplicate_username(self):
        User.objects.create_user(
            username="testuser", password="testpass123", email="t@test.com"
        )
        response = self.client.post("/inscription/", {
            "username": "testuser",
            "email": "other@test.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        })
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )

    def test_logout_post(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post("/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_logout_get_rejected(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 405)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@test.com"
        )
        self.client.login(username="testuser", password="testpass123")

    def test_profile_page_status(self):
        response = self.client.get("/profil/")
        self.assertEqual(response.status_code, 200)

    def test_profile_update(self):
        response = self.client.post("/profil/", {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "test@test.com",
            "phone": "+22501020304",
            "bio": "Développeur",
            "location": "Abidjan",
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jean")
        self.assertEqual(self.user.last_name, "Dupont")
        self.assertEqual(self.user.phone, "+22501020304")

    def test_profile_requires_login(self):
        self.client.logout()
        response = self.client.get("/profil/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
