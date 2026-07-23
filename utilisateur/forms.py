from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm

User = get_user_model()


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "bio", "date_of_birth", "location"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Prénom"}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Nom"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "Email"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "Téléphone"}),
            "bio": forms.Textarea(attrs={"class": "form-input", "placeholder": "Bio", "rows": 3}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "location": forms.TextInput(attrs={"class": "form-input", "placeholder": "Localisation"}),
        }
