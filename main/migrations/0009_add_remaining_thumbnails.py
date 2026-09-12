from django.db import migrations


THUMBNAILS = {
    'Asadha Event – Vihara Gunadharma': '/static/img/experience/asadha-event-vihara-gunadharma.jpg',
    'Academic & Teaching Staff – BETIS Fasilkom UI': '/static/img/experience/betis-fasilkom-ui.jpg',
    'Staff of Academy Division (DSAI) – COMPFEST': '/static/img/experience/compfest-dsai.jpg',
    'VPIC of Mentor Division – DDP0': '/static/img/experience/vpic-mentor-ddp0.jpg',
    'Business Development Staff – Open House Fasilkom UI': '/static/img/experience/open-house-fasilkom-ui.jpg',
}


def add_thumbnails(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    for title, thumbnail in THUMBNAILS.items():
        Experience.objects.filter(title=title).update(thumbnail=thumbnail)


def remove_thumbnails(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Experience.objects.filter(title__in=THUMBNAILS.keys()).update(thumbnail=None)


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_add_more_thumbnails'),
    ]

    operations = [
        migrations.RunPython(add_thumbnails, remove_thumbnails),
    ]
