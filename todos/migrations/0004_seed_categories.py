from django.db import migrations

CATEGORIES = [
    {"nom": "Études", "icon": "📚", "description": "Devoirs, examens, révisions", "couleur": "#6c5ce7"},
    {"nom": "Travail", "icon": "💼", "description": "Missions professionnelles", "couleur": "#0984e3"},
    {"nom": "Développement", "icon": "💻", "description": "Programmation, projets, bugs", "couleur": "#00b894"},
    {"nom": "Projets", "icon": "🚀", "description": "Projets personnels ou d'équipe", "couleur": "#e17055"},
    {"nom": "Courses", "icon": "🛒", "description": "Achats alimentaires ou divers", "couleur": "#fdcb6e"},
    {"nom": "Maison", "icon": "🏠", "description": "Ménage, bricolage, jardinage", "couleur": "#00cec9"},
    {"nom": "Finances", "icon": "💰", "description": "Factures, budget, impôts", "couleur": "#55efc4"},
    {"nom": "Santé", "icon": "❤️", "description": "Rendez-vous médicaux, médicaments", "couleur": "#d63031"},
    {"nom": "Sport", "icon": "🏃", "description": "Entraînements, activités physiques", "couleur": "#fd79a8"},
    {"nom": "Cuisine", "icon": "🍽️", "description": "Préparation des repas", "couleur": "#e17055"},
    {"nom": "Voyage", "icon": "✈️", "description": "Réservations, bagages", "couleur": "#74b9ff"},
    {"nom": "Famille", "icon": "👨‍👩‍👧", "description": "Activités familiales", "couleur": "#a29bfe"},
    {"nom": "Amis", "icon": "👥", "description": "Sorties, anniversaires", "couleur": "#fab1a0"},
    {"nom": "Appels", "icon": "📞", "description": "Personnes à contacter", "couleur": "#81ecec"},
    {"nom": "Emails", "icon": "📧", "description": "Répondre ou envoyer des emails", "couleur": "#636e72"},
    {"nom": "Rendez-vous", "icon": "📅", "description": "Réunions, consultations", "couleur": "#00b894"},
    {"nom": "Objectifs", "icon": "🎯", "description": "Objectifs personnels", "couleur": "#d63031"},
    {"nom": "Lecture", "icon": "📖", "description": "Livres et articles à lire", "couleur": "#6c5ce7"},
    {"nom": "Loisirs", "icon": "🎬", "description": "Films, jeux, séries", "couleur": "#fd79a8"},
    {"nom": "Musique", "icon": "🎵", "description": "Pratique ou écoute", "couleur": "#a29bfe"},
    {"nom": "Maintenance", "icon": "🛠️", "description": "Réparations, mises à jour", "couleur": "#636e72"},
    {"nom": "Animaux", "icon": "🐶", "description": "Soins des animaux", "couleur": "#fab1a0"},
    {"nom": "Transport", "icon": "🚗", "description": "Entretien du véhicule", "couleur": "#0984e3"},
    {"nom": "Administration", "icon": "📂", "description": "Documents officiels", "couleur": "#2d3436"},
    {"nom": "Nettoyage", "icon": "🧹", "description": "Tâches ménagères", "couleur": "#00cec9"},
    {"nom": "Événements", "icon": "🎉", "description": "Mariages, fêtes, conférences", "couleur": "#fdcb6e"},
    {"nom": "Idées", "icon": "💡", "description": "Notes et inspirations", "couleur": "#fdcb6e"},
    {"nom": "Rappels", "icon": "🔔", "description": "Choses importantes à ne pas oublier", "couleur": "#d63031"},
    {"nom": "Shopping", "icon": "🛍️", "description": "Vêtements, électronique, cadeaux", "couleur": "#e84393"},
    {"nom": "Développement personnel", "icon": "🌱", "description": "Formations, habitudes, méditation", "couleur": "#00b894"},
]


def forward(apps, schema_editor):
    Categorie = apps.get_model("todos", "Categorie")
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
    Categorie = apps.get_model("todos", "Categorie")
    Categorie.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("todos", "0003_add_categorie_fields"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
