from django.db import migrations
from django.utils import timezone


EXPERIENCES = [
    {
        'title': 'VPIC of Mentor Division – DDP0',
        'description': (
            'Developed structured SOPs and mentoring frameworks that ensured '
            'consistent, high-quality guidance across the mentoring team.'
        ),
        'category': 'volunteer',
        'ongoing': True,
    },
    {
        'title': 'Staff of Academy Division (DSAI) – COMPFEST',
        'description': (
            'Managed relations with industry mentors and lecturers, designed '
            'the participant selection framework, and oversaw real-time '
            'event operations, keeping all technical and logistical sessions '
            'running smoothly.'
        ),
        'category': 'volunteer',
        'ongoing': True,
    },
    {
        'title': 'Academic & Teaching Staff – BETIS Fasilkom UI',
        'description': (
            'Simplified complex course material into structured teaching '
            'modules and delivered learning sessions that helped students '
            'grasp difficult topics more easily.'
        ),
        'category': 'part-time',
        'ongoing': False,
    },
    {
        'title': 'Business Development Staff – Open House Fasilkom UI',
        'description': (
            'Coordinated with external vendors and liaised between the '
            'committee and partners to keep event logistics running without '
            'major issues.'
        ),
        'category': 'volunteer',
        'ongoing': False,
    },
    {
        'title': 'SPB – Kahf (Paragon Corp) at PRJ 2026',
        'description': (
            'Engaged directly with event visitors to promote brand products '
            'in a high-traffic, fast-paced environment, successfully '
            'driving on-site customer interest.'
        ),
        'category': 'freelance',
        'ongoing': False,
        'thumbnail': '/static/img/experience/kahf-prj-2026.jpg',
    },
    {
        'title': 'Talent & SPB – Byon Combat (Kahf)',
        'description': (
            'Represented the brand as talent and SPB at the Byon Combat '
            'event, engaging directly with attendees.'
        ),
        'category': 'freelance',
        'ongoing': False,
        'thumbnail': '/static/img/experience/byon-combat-showbiz-8.jpg',
    },
    {
        'title': 'Usher – Mitski Live in Jakarta',
        'description': (
            'Managed audience flow and coordinated with the event team '
            'under time pressure to keep the concert running smoothly for '
            'attendees.'
        ),
        'category': 'freelance',
        'ongoing': False,
        'thumbnail': '/static/img/experience/usher-mitski-concert.jpg',
    },
    {
        'title': 'Usher – Bernadya Concert',
        'description': (
            'Managed audience flow and coordinated with the event team '
            'under time pressure to keep the concert running smoothly for '
            'attendees.'
        ),
        'category': 'freelance',
        'ongoing': False,
        'thumbnail': '/static/img/experience/usher-bernadya-concert.jpg',
    },
    {
        'title': 'Usher / SPB / Talent – JSD Blok M Festival (Prabu Indonesia)',
        'description': (
            'Took on multiple rotating roles across audience management, '
            'brand promotion, and on-stage duties, adapting quickly as '
            'event needs shifted.'
        ),
        'category': 'freelance',
        'ongoing': False,
        'thumbnail': '/static/img/experience/prabu-jsd.jpg',
    },
    {
        'title': 'Panti Werdha Muslim Rumah Oma',
        'description': (
            'Worked as field crew preparing equipment and logistics, while '
            'engaging the elderly residents through conversation and humor '
            'to keep the event warm and well-run.'
        ),
        'category': 'volunteer',
        'ongoing': False,
    },
    {
        'title': 'Panti Asuhan Hati Suci (Open Donation Event)',
        'description': 'Volunteered as a performer to support the fundraising event.',
        'category': 'volunteer',
        'ongoing': False,
    },
    {
        'title': 'Smandu Idol Season 5',
        'description': 'Volunteered as a performer.',
        'category': 'volunteer',
        'ongoing': False,
    },
    {
        'title': 'Asadha Event – Vihara Gunadharma',
        'description': 'Volunteered as a performer.',
        'category': 'volunteer',
        'ongoing': False,
    },
    {
        'title': 'Self-Started Floral Business',
        'description': (
            'Managed end-to-end business operations including product '
            'assembly and order fulfillment, executed social media '
            'marketing to build brand awareness, and maintained direct '
            'communication with customers to ensure service quality.'
        ),
        'category': 'full-time',
        'ongoing': True,
    },
]


def seed_experience(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    # Clear out any leftover manual/test rows so the real list isn't duplicated.
    Experience.objects.all().delete()

    now = timezone.now()
    for data in EXPERIENCES:
        Experience.objects.create(
            title=data['title'],
            description=data['description'],
            category=data['category'],
            thumbnail=data.get('thumbnail'),
            ended_at=None if data['ongoing'] else now,
        )


def remove_seeded_experience(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Experience.objects.filter(
        title__in=[e['title'] for e in EXPERIENCES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_experience_thumbnail'),
    ]

    operations = [
        migrations.RunPython(seed_experience, remove_seeded_experience),
    ]
