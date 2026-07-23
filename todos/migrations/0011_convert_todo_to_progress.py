from django.db import migrations


def convert_todo_to_progress(apps, schema_editor):
    Tache = apps.get_model('todos', 'Tache')
    Tache.objects.filter(status='todo').update(status='progress')


def reverse(apps, schema_editor):
    Tache = apps.get_model('todos', 'Tache')
    Tache.objects.filter(status='progress').update(status='todo')


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0010_alter_tache_status'),
    ]

    operations = [
        migrations.RunPython(convert_todo_to_progress, reverse),
    ]
