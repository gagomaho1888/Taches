from django.db import migrations

CATEGORIES_TO_RESTORE = [
    {"nom": "Cuisine", "icon": "🍽️", "description": "Préparation des repas", "couleur": "#e17055"},
    {"nom": "Nettoyage", "icon": "🧹", "description": "Tâches ménagères", "couleur": "#00cec9"},
    {"nom": "Maintenance", "icon": "🛠️", "description": "Réparations, mises à jour", "couleur": "#636e72"},
    {"nom": "Shopping", "icon": "🛍️", "description": "Vêtements, électronique, cadeaux", "couleur": "#e84393"},
    {"nom": "Appels", "icon": "📞", "description": "Personnes à contacter", "couleur": "#81ecec"},
    {"nom": "Emails", "icon": "📧", "description": "Répondre ou envoyer des emails", "couleur": "#636e72"},
    {"nom": "Musique", "icon": "🎵", "description": "Pratique ou écoute", "couleur": "#a29bfe"},
    {"nom": "Lecture", "icon": "📖", "description": "Livres et articles à lire", "couleur": "#6c5ce7"},
]

# Remettre les descriptions originales des catégories mergées
CATEGORIES_TO_REVERT = [
    {"nom": "Courses", "icon": "🛒", "description": "Achats alimentaires ou divers", "couleur": "#fdcb6e"},
    {"nom": "Maison", "icon": "🏠", "description": "Ménage, bricolage, jardinage", "couleur": "#00cec9"},
    {"nom": "Rendez-vous", "icon": "📅", "description": "Réunions, consultations", "couleur": "#00b894"},
    {"nom": "Loisirs", "icon": "🎬", "description": "Films, jeux, séries", "couleur": "#fd79a8"},
]


def forward(apps, schema_editor):
    Categorie = apps.get_model("todos", "Categorie")
    for cat in CATEGORIES_TO_RESTORE + CATEGORIES_TO_REVERT:
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
    Categorie.objects.filter(nom__in=[c["nom"] for c in CATEGORIES_TO_RESTORE]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("todos", "0005_merge_categories"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
