from django.db import migrations

EMOJI_TO_ICON = {
    "📚": "book",
    "💼": "briefcase",
    "💻": "code",
    "🚀": "rocket",
    "🛒": "cart",
    "🏠": "home",
    "💰": "coin",
    "❤️": "heart",
    "🏃": "run",
    "🍽️": "utensils",
    "✈️": "plane",
    "👨‍👩‍👧": "family",
    "👥": "users",
    "📞": "phone",
    "📧": "mail",
    "📅": "calendar",
    "🎯": "target",
    "📖": "book-open",
    "🎬": "film",
    "🎵": "music",
    "🛠️": "wrench",
    "🐶": "paw",
    "🚗": "car",
    "📂": "folder",
    "🧹": "broom",
    "🎉": "party",
    "💡": "bulb",
    "🔔": "bell",
    "🛍️": "bag",
    "🌱": "seedling",
}


def forward(apps, schema_editor):
    Categorie = apps.get_model("todos", "Categorie")
    for cat in Categorie.objects.all():
        icon_id = EMOJI_TO_ICON.get(cat.icon, "")
        if icon_id:
            cat.icon = icon_id
            cat.save(update_fields=["icon"])


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("todos", "0007_update_icon_field"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
