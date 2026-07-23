from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("inscription/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profil/", views.profile_view, name="profile"),
]
