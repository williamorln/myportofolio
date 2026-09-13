from django.db import migrations


TITLE = 'Academic & Teaching Staff – BETIS Fasilkom UI'


def set_volunteer(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Experience.objects.filter(title=TITLE).update(category='volunteer')


def set_part_time(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Experience.objects.filter(title=TITLE).update(category='part-time')


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_update_sabang_merauke_description'),
    ]

    operations = [
        migrations.RunPython(set_volunteer, set_part_time),
    ]
