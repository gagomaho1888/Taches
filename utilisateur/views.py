from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import UserCreationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accueil")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next") or "accueil")
        else:
            messages.error(request, "Identifiants incorrects.")

    return render(request, "registration/login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("accueil")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé avec succès.")
            return redirect("accueil")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Vous êtes déconnecté.")
    return redirect("login")
