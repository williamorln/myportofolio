from django.db import migrations


THUMBNAILS = {
    'Panti Werdha Muslim Rumah Oma': '/static/img/experience/panti-werdha-muslim-rumah-oma.jpg',
    'Self-Started Floral Business': '/static/img/experience/self-started-floral-business.jpg',
    'Panti Asuhan Hati Suci (Open Donation Event)': '/static/img/experience/panti-asuhan-hati-suci.jpg',
    'Smandu Idol Season 5': '/static/img/experience/smandu-idol-season-5.jpg',
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
        ('main', '0007_add_sabang_merauke'),
    ]

    operations = [
        migrations.RunPython(add_thumbnails, remove_thumbnails),
    ]
