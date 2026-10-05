import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


def _is_editor(user):
    return (
        user.is_authenticated
        and user.groups.filter(name='Editor').exists()
    )


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


def _filtered_experiences(request):
    experiences = Experience.objects.prefetch_related('starred_by').order_by(
        'category', 'title', 'pk',
    )
    title = request.GET.get('title', '').strip()
    status = request.GET.get('status', '')
    if title:
        experiences = experiences.filter(title__icontains=title)
    if status in ('ongoing', 'completed'):
        experiences = experiences.filter(ended_at__isnull=(status == 'ongoing'))
    return experiences


def show_experience(request):
    experiences = list(_filtered_experiences(request))
    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'experience_list': experiences,
        'title_query': request.GET.get('title', '').strip(),
        'status_query': request.GET.get('status', ''),
        'is_editor': _is_editor(request.user),
        'active_page': 'experience',
    }
    return render(request, 'experience.html', context)


def get_experience_json(request):
    """Return filtered experience data with request-specific star details."""
    data = []
    for experience in _filtered_experiences(request):
        starred_users = list(experience.starred_by.all())
        data.append({
            'pk': str(experience.pk),
            'fields': {
                'title': experience.title,
                'description': experience.description,
                'category': experience.category,
                'category_display': experience.get_category_display(),
                'thumbnail': experience.thumbnail,
                'started_at': experience.started_at.isoformat(),
                'ended_at': (
                    experience.ended_at.isoformat()
                    if experience.ended_at else None
                ),
                'is_ongoing': experience.is_ongoing,
                'star_count': len(starred_users),
                'is_starred': (
                    request.user.is_authenticated
                    and any(user.pk == request.user.pk for user in starred_users)
                ),
                'starred_by_names': ', '.join(
                    user.username for user in starred_users
                ),
            },
        })
    return JsonResponse(data, safe=False)


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
@login_required(login_url='/login/')
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    return _experience_form(request)


@require_POST
def create_experience_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {
                'message': (
                    'Hanya pemilik portofolio yang dapat menambahkan pengalaman.'
                ),
            },
            status=403,
        )

    form = ExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {
                'message': 'Pengalaman berhasil ditambahkan.',
                'pk': str(experience.pk),
            },
            status=201,
        )

    return JsonResponse({'errors': form.errors.get_json_data()}, status=400)


@require_http_methods(['GET', 'POST'])
@login_required(login_url='/login/')
def update_experience(request, experience_id):
    if not (request.user.is_superuser or _is_editor(request.user)):
        raise PermissionDenied

    return _experience_form(request, get_object_or_404(Experience, pk=experience_id))


@require_http_methods(['GET', 'POST'])
@login_required(login_url='/login/')
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == 'POST':
        experience.delete()
        messages.success(request, 'Pengalaman berhasil dihapus.')
        return redirect('main:show_experience')
    return render(request, 'experience_confirm_delete.html', _experience_context(experience=experience))


@login_required(login_url='/login/')
@require_http_methods(['POST'])
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
        is_starred = False
    else:
        experience.starred_by.add(request.user)
        is_starred = True

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'is_starred': is_starred,
            'star_count': experience.starred_by.count(),
        })

    return redirect('main:show_experience')


def get_projects_json(request):
    title_query = request.GET.get('title', '').strip()
    projects = Project.objects.prefetch_related('starred_by').order_by(
        '-created_at', 'title', 'pk',
    )

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        starred_users = list(project.starred_by.all())
        data.append({
            'pk': str(project.pk),
            'fields': {
                'title': project.title,
                'problem': project.problem,
                'solution': project.solution,
                'tech_stack': project.tech_stack,
                'project_url': project.project_url,
                'star_count': len(starred_users),
                'is_starred': (
                    request.user.is_authenticated
                    and any(user.pk == request.user.pk for user in starred_users)
                ),
                'starred_by_names': ', '.join(
                    user.username for user in starred_users
                ),
            },
        })

    return JsonResponse(data, safe=False)


def show_projects(request):
    title_query = request.GET.get('title', '').strip()

    context = {
        'name': 'William Orlando',
        'npm': '2506657390',
        'study_program': 'S1 Sistem Informasi',
        'title_query': title_query,
        'form': ProjectForm(),
        'active_page': 'projects',
    }
    return render(request, 'projects.html', context)


@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {'message': 'Hanya pemilik portofolio yang dapat menambahkan proyek.'},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {'message': 'Proyek berhasil ditambahkan.', 'pk': str(project.pk)},
            status=201,
        )

    return JsonResponse({'errors': form.errors.get_json_data()}, status=400)


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
