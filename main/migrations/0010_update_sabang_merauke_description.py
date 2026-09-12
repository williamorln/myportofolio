from django.db import migrations


TITLE = 'SPB – Pagelaran Sabang Merauke (Prabu)'

NEW_DESCRIPTION = (
    'Represented Prabu Indonesia as SPB at Pagelaran Sabang Merauke, '
    'engaging directly with high-profile guests including the '
    'President Director of OJK (Otoritas Jasa Keuangan) and several '
    'government ministers. Also featured as an interviewee in a CNN '
    'Indonesia broadcast segment covering the event.'
)

OLD_DESCRIPTION = (
    'Represented Prabu Indonesia as SPB at Pagelaran Sabang '
    'Merauke, engaging directly with visitors to promote the '
    'brand.'
)


def update_description(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Experience.objects.filter(title=TITLE).update(description=NEW_DESCRIPTION)


def revert_description(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Experience.objects.filter(title=TITLE).update(description=OLD_DESCRIPTION)


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_add_remaining_thumbnails'),
    ]

    operations = [
        migrations.RunPython(update_description, revert_description),
    ]
