from django import forms
from django.utils import timezone
from .models import Tache, SousTache, Categorie, Comment, Groupe


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = [
            "title",
            "description",
            "categorie",
            "priority",
            "start_date",
            "deadline",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Titre de la tâche",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-input",
                "placeholder": "Description (optionnel)",
                "rows": 4,
            }),
            "categorie": forms.Select(attrs={
                "class": "form-input categorie-select",
            }),
            "priority": forms.RadioSelect(attrs={
                "class": "priority-radio",
            }),
            "start_date": forms.DateTimeInput(attrs={
                "class": "form-input",
                "type": "datetime-local",
            }),
            "deadline": forms.DateTimeInput(attrs={
                "class": "form-input",
                "type": "datetime-local",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categorie"].empty_label = "-- Choisir une catégorie --"
        self.fields["categorie"].queryset = Categorie.objects.all().order_by("nom")

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")
        if start_date and start_date < timezone.now():
            raise forms.ValidationError("La date de début ne peut pas être dans le passé.")
        return start_date

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline:
            if deadline < timezone.now():
                raise forms.ValidationError("L'échéance ne peut pas être dans le passé.")
        return deadline

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        deadline = cleaned_data.get("deadline")
        if start_date and deadline and start_date > deadline:
            raise forms.ValidationError(
                "La date de début doit être antérieure à l'échéance."
            )
        return cleaned_data


class SousTacheForm(forms.ModelForm):
    class Meta:
        model = SousTache
        fields = ["title"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Sous-tâche...",
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-input",
                "placeholder": "Écrire un commentaire...",
                "rows": 3,
            }),
        }
        labels = {
            "content": "",
        }


class GroupeForm(forms.ModelForm):
    class Meta:
        model = Groupe
        fields = ["nom", "description"]
        widgets = {
            "nom": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Nom du groupe",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-input",
                "placeholder": "Description (optionnel)",
                "rows": 3,
            }),
        }


class RejoindreGroupeForm(forms.Form):
    code = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Code du groupe",
        }),
        label="Code du groupe",
    )


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ["nom", "description"]
        widgets = {
            "nom": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Nom de la catégorie",
            }),
            "description": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Description (optionnel)",
            }),
        }


class AssignTacheForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Titre de la tâche",
        }),
        label="Titre",
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-input",
            "placeholder": "Description (optionnel)",
            "rows": 3,
        }),
        label="Description",
    )
    assigned_to = forms.IntegerField(
        widget=forms.Select(attrs={
            "class": "form-input",
        }),
        label="Assigner à",
    )
    priority = forms.ChoiceField(
        choices=Tache.PRIORITY,
        initial="medium",
        widget=forms.RadioSelect(attrs={
            "class": "priority-radio",
        }),
        label="Priorité",
    )
    deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            "class": "form-input",
            "type": "datetime-local",
        }),
        label="Échéance",
    )
