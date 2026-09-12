from django.db import migrations


def remove_qrmenuku(apps, schema_editor):
    Project = apps.get_model('main', 'Project')
    Project.objects.filter(
        title='QRMenuKu – Business Plan & Product Development'
    ).delete()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_seed_projects'),
    ]

    operations = [
        migrations.RunPython(remove_qrmenuku, noop_reverse),
    ]
