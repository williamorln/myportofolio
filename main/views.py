import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


def show_main(request):
    last_login = request.COOKIES.get(
        'last_login', 'Belum ada sesi login / Cookie tidak ditemukan',
    )
    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'bio': (
            'Building digital solutions through technology, leadership, '
            'and problem solving.'
        ),
        'active_page': 'main',
        'last_login': last_login,
    }
    return render(request, 'index.html', context)


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Akun berhasil dibuat. Silakan login.')
        return redirect('main:login')

    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'form': form,
    }
    return render(request, 'register.html', context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        response = redirect('main:show_main')
        response.set_cookie(
            'last_login',
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )
        return response

    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'form': form,
    }
    return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    response = redirect('main:show_main')
    response.delete_cookie('last_login')
    return response


def show_experience(request):
    # Use the same filtered JSON delivery as the public API, then restore objects
    # so template properties (including is_ongoing) remain available.
    json_response = get_experience_json(request)
    experiences = [item.object for item in serializers.deserialize(
        'json', json_response.content.decode('utf-8'),
    )]
    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'experience_list': experiences,
        'title_query': request.GET.get('title', '').strip(),
        'status_query': request.GET.get('status', ''),
        'active_page': 'experience',
    }
    return render(request, 'experience.html', context)


def get_experience_json(request):
    """Deliver a consistently ordered, optionally filtered experience collection."""
    experiences = Experience.objects.all().order_by('category', 'title', 'pk')
    title = request.GET.get('title', '').strip()
    status = request.GET.get('status', '')
    if title:
        experiences = experiences.filter(title__icontains=title)
    if status in ('ongoing', 'completed'):
        experiences = experiences.filter(ended_at__isnull=(status == 'ongoing'))
    return HttpResponse(serializers.serialize('json', experiences), content_type='application/json')


def _experience_context(**extra):
    return {
        'name': 'William Orlando', 'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi', 'active_page': 'experience',
        **extra,
    }


def _experience_form(request, instance=None):
    """Share validation and rendering while binding edits to the existing row."""
    form = ExperienceForm(
        request.POST if request.method == 'POST' else None, instance=instance,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Pengalaman berhasil diperbarui.' if instance else 'Pengalaman berhasil ditambahkan.')
        return redirect('main:show_experience')
    return render(request, 'experience_form.html', _experience_context(
        form=form, editing=instance is not None,
    ))


@require_http_methods(['GET', 'POST'])
def create_experience(request):
    return _experience_form(request)


@require_http_methods(['GET', 'POST'])
def update_experience(request, experience_id):
    return _experience_form(request, get_object_or_404(Experience, pk=experience_id))


@require_http_methods(['GET', 'POST'])
def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == 'POST':
        experience.delete()
        messages.success(request, 'Pengalaman berhasil dihapus.')
        return redirect('main:show_experience')
    return render(request, 'experience_confirm_delete.html', _experience_context(experience=experience))


def get_projects_json(request):
    title_query = request.GET.get('title', '').strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize(
        'json', projects, use_natural_foreign_keys=True,
    )
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


@login_required(login_url='/login/')
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url='/login/')
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project berhasil dihapus!')
        return redirect('main:show_projects')

    return redirect('main:show_projects')


@login_required(login_url='/login/')
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect('main:show_projects')
