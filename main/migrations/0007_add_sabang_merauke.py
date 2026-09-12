from django.db import migrations
from django.utils import timezone


TITLE = 'SPB – Pagelaran Sabang Merauke (Prabu)'


def add_experience(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Experience.objects.create(
        title=TITLE,
        description=(
            'Represented Prabu Indonesia as SPB at Pagelaran Sabang '
            'Merauke, engaging directly with visitors to promote the '
            'brand.'
        ),
        category='freelance',
        thumbnail='/static/img/experience/pagelaran-sabang-merauke-prabu.jpg',
        ended_at=timezone.now(),
    )


def remove_experience(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Experience.objects.filter(title=TITLE).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_seed_experience'),
    ]

    operations = [
        migrations.RunPython(add_experience, remove_experience),
    ]
