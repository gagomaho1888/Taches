from django.db import migrations

CATEGORIES = [
    {"nom": "Études", "icon": "📚", "description": "Devoirs, examens, révisions", "couleur": "#6c5ce7"},
    {"nom": "Travail", "icon": "💼", "description": "Missions professionnelles", "couleur": "#0984e3"},
    {"nom": "Développement", "icon": "💻", "description": "Programmation, projets, bugs", "couleur": "#00b894"},
    {"nom": "Projets", "icon": "🚀", "description": "Projets personnels ou d'équipe", "couleur": "#e17055"},
    {"nom": "Courses", "icon": "🛒", "description": "Achats alimentaires, vêtements, divers", "couleur": "#fdcb6e"},
    {"nom": "Maison", "icon": "🏠", "description": "Ménage, bricolage, cuisine, jardinage", "couleur": "#00cec9"},
    {"nom": "Finances", "icon": "💰", "description": "Factures, budget, impôts", "couleur": "#55efc4"},
    {"nom": "Santé", "icon": "❤️", "description": "Rendez-vous médicaux, médicaments", "couleur": "#d63031"},
    {"nom": "Sport", "icon": "🏃", "description": "Entraînements, activités physiques", "couleur": "#fd79a8"},
    {"nom": "Voyage", "icon": "✈️", "description": "Réservations, bagages", "couleur": "#74b9ff"},
    {"nom": "Famille", "icon": "👨‍👩‍👧", "description": "Activités familiales", "couleur": "#a29bfe"},
    {"nom": "Amis", "icon": "👥", "description": "Sorties, anniversaires", "couleur": "#fab1a0"},
    {"nom": "Rendez-vous", "icon": "📅", "description": "Réunions, appels, emails", "couleur": "#00b894"},
    {"nom": "Objectifs", "icon": "🎯", "description": "Objectifs personnels", "couleur": "#d63031"},
    {"nom": "Loisirs", "icon": "🎬", "description": "Films, jeux, musique, lecture", "couleur": "#fd79a8"},
    {"nom": "Animaux", "icon": "🐶", "description": "Soins des animaux", "couleur": "#fab1a0"},
    {"nom": "Transport", "icon": "🚗", "description": "Entretien du véhicule", "couleur": "#0984e3"},
    {"nom": "Administration", "icon": "📂", "description": "Documents officiels", "couleur": "#2d3436"},
    {"nom": "Événements", "icon": "🎉", "description": "Mariages, fêtes, conférences", "couleur": "#fdcb6e"},
    {"nom": "Idées", "icon": "💡", "description": "Notes et inspirations", "couleur": "#fdcb6e"},
    {"nom": "Rappels", "icon": "🔔", "description": "Choses importantes à ne pas oublier", "couleur": "#d63031"},
    {"nom": "Développement personnel", "icon": "🌱", "description": "Formations, habitudes, méditation", "couleur": "#00b894"},
]

TO_DELETE = ["Cuisine", "Nettoyage", "Maintenance", "Shopping", "Appels", "Emails", "Musique", "Lecture"]


def forward(apps, schema_editor):
    Categorie = apps.get_model("todos", "Categorie")
    Categorie.objects.filter(nom__in=TO_DELETE).delete()
    for cat in CATEGORIES:
        Categorie.objects.update_or_create(
            nom=cat["nom"],
            defaults={
                "icon": cat["icon"],
                "description": cat["description"],
                "couleur": cat["couleur"],
            },
        )


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("todos", "0004_seed_categories"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
