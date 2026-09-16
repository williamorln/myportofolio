from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ProjectForm
from main.models import Experience, Project


def show_main(request):
    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'bio': (
            'Building digital solutions through technology, leadership, '
            'and problem solving.'
        ),
        'active_page': 'main',
    }
    return render(request, 'index.html', context)


def show_experience(request):
    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'experience_list': Experience.objects.all().order_by('category', 'title'),
        'active_page': 'experience',
    }
    return render(request, 'experience.html', context)


def get_projects_json(request):
    title_query = request.GET.get('title', '').strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize('json', projects)
    return HttpResponse(projects_json, content_type='application/json')


def show_projects(request):
    json_response = get_projects_json(request)
    projects = serializers.deserialize(
        'json',
        json_response.content.decode('utf-8'),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get('title', '').strip()

    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'project_list': projects,
        'title_query': title_query,
        'active_page': 'projects',
    }
    return render(request, 'projects.html', context)


def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Proyek baru berhasil ditambahkan!')
        return redirect('main:show_projects')

    context = {
        'name': 'William Orlando',
        'form': form,
        'active_page': 'projects',
    }
    return render(request, 'projects_form.html', context)


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project berhasil dihapus!')
        return redirect('main:show_projects')

    return redirect('main:show_projects')
