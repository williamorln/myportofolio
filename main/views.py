from django.shortcuts import render

from main.models import Experience


def show_main(request):
    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'bio': (
            'Building digital solutions through technology, leadership, '
            'and problem solving.'
        ),
    }
    return render(request, 'index.html', context)


def show_experience(request):
    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'experience_list': Experience.objects.all(),
    }
    return render(request, 'experience.html', context)
