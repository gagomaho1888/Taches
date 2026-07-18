from django import forms
from django.utils import timezone
from .models import Tache, SousTache, Categorie, Comment, Groupe, MembreGroupe


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

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline:
            if deadline < timezone.now():
                raise forms.ValidationError("L'échéance ne peut pas être dans le passé.")
        return deadline


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
        max_length=8,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Code du groupe",
        }),
        label="Code du groupe",
    )


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
