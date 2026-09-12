from django.db import migrations


PROJECTS = [
    {
        'title': 'SCELE Notifier',
        'problem': (
            "SCELE, Fasilkom UI's course platform, doesn't proactively "
            "notify students about new assignments or forum activity "
            "— and its RSS feeds are disabled."
        ),
        'solution': (
            'Built a Telegram bot that logs into SCELE via session '
            'scraping, monitors the Timeline and forum activity, and '
            "pushes real-time notifications — reverse-engineered "
            "SCELE's internal AJAX endpoint from scratch to make it work."
        ),
        'tech_stack': 'Python · Telegram Bot API · Web Scraping',
    },
    {
        'title': 'Life OS',
        'problem': (
            "Academic reminders alone don't cover the rest of daily "
            'planning — tasks, goals, and reminders end up scattered '
            'across different tools.'
        ),
        'solution': (
            'Expanded the SCELE Notifier into a broader personal assistant '
            'bot covering reminders, goal tracking, and daily planning as '
            'a lightweight, all-in-one productivity system.'
        ),
        'tech_stack': 'Python · Telegram Bot API',
    },
    {
        'title': 'Omnichannel AI Chatbot',
        'problem': (
            "Businesses need a chatbot that isn't locked into a single "
            'messaging platform.'
        ),
        'solution': (
            'Built a chatbot system with an extensive feature set designed '
            'to operate across multiple messaging channels, rather than '
            'being tied to one.'
        ),
        'tech_stack': 'Python · Chatbot / NLP Tooling',
    },
    {
        'title': 'PO Workflow System – Prabu',
        'problem': (
            'Prabu, a shoe brand, managed its purchase order process '
            'manually and in a fragmented way.'
        ),
        'solution': (
            'Designed and built a workflow system to manage the PO process '
            'end-to-end, turning it into a structured, repeatable system.'
        ),
        'tech_stack': 'Workflow & System Design',
    },
    {
        'title': 'Clipping Automation',
        'problem': (
            'A content clipping business needed to cut down on repetitive '
            'manual work in processing clipped content at scale.'
        ),
        'solution': (
            'Built automation tooling to streamline the repetitive parts '
            'of managing and processing clipped content.'
        ),
        'tech_stack': 'Automation Scripting',
    },
    {
        'title': 'QRMenuKu – Business Plan & Product Development',
        'problem': 'Traditional F&B SME ordering processes are slow and inefficient.',
        'solution': (
            'Collaborated in a team to design a digital ordering system '
            'with an analytics dashboard and payment gateway integration, '
            'contributing to the business model and operational workflow '
            'design.'
        ),
        'tech_stack': 'Product & Business Design',
    },
    {
        'title': 'Personal Portfolio Website',
        'problem': (
            'Needed a live, continuously-updated portfolio to showcase '
            'skills and experience for academic and professional purposes.'
        ),
        'solution': (
            'Built and iterated on this site from scratch across weekly '
            'assignments for the Pemrograman Berbasis Platform course.'
        ),
        'tech_stack': 'Django · HTML5 · CSS3',
    },
]


def seed_projects(apps, schema_editor):
    Project = apps.get_model('main', 'Project')
    for data in PROJECTS:
        Project.objects.create(**data)


def remove_seeded_projects(apps, schema_editor):
    Project = apps.get_model('main', 'Project')
    Project.objects.filter(title__in=[p['title'] for p in PROJECTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_project'),
    ]

    operations = [
        migrations.RunPython(seed_projects, remove_seeded_projects),
    ]
