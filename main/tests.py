import uuid
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.core import serializers
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project
from main.forms import ExperienceForm, ProjectForm


class ExperienceFlowTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            'experience_owner', 'owner@example.com', 'SafePass123!',
        )
        self.client.force_login(self.admin)
        self.payload = {
            'title': 'Research Assistant', 'description': 'Analisis data penelitian.',
            'category': 'research', 'thumbnail': '/static/img/research.jpg',
            'ended_at': '',
        }
        self.experience = Experience.objects.create(
            title='Unique Volunteer', description='Kegiatan sosial.', category='volunteer',
        )

    def url(self, action):
        return reverse(f'main:{action}_experience', args=[self.experience.pk])

    def test_form_includes_all_editable_fields(self):
        self.assertEqual(set(ExperienceForm().fields), {
            'title', 'description', 'category', 'thumbnail', 'ended_at',
        })

    def test_create_then_update_preserves_identity_and_count(self):
        before = Experience.objects.count()
        response = self.client.post(reverse('main:create_experience'), self.payload)
        self.assertRedirects(response, reverse('main:show_experience'))
        self.experience = Experience.objects.get(title=self.payload['title'])
        started_at = self.experience.started_at
        response = self.client.get(self.url('update'))
        self.assertContains(response, self.payload['title'])
        self.assertTemplateUsed(response, 'base.html')
        payload = {**self.payload, 'title': 'Updated Research', 'ended_at': '2026-09-20T12:30'}
        self.assertRedirects(self.client.post(self.url('update'), payload), reverse('main:show_experience'))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, payload['title'])
        self.assertEqual(self.experience.started_at, started_at)
        self.assertFalse(self.experience.is_ongoing)
        self.assertEqual(Experience.objects.count(), before + 1)
        response = self.client.get(self.url('update'))
        self.assertContains(response, '2026-09-20T12:30')
        self.client.post(self.url('update'), self.payload)
        self.experience.refresh_from_db()
        self.assertTrue(self.experience.is_ongoing)

    def test_invalid_forms_do_not_write_and_preserve_input(self):
        before = Experience.objects.count()
        for invalid in ({'title': ''}, {'category': 'unknown'}, {'ended_at': 'not a date'}):
            with self.subTest(invalid=invalid):
                response = self.client.post(reverse('main:create_experience'), {**self.payload, **invalid})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].errors)
                self.assertContains(response, self.payload['description'])
        response = self.client.post(self.url('update'), {**self.payload, 'title': ''})
        self.assertTrue(response.context['form'].errors)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, 'Unique Volunteer')
        self.assertEqual(Experience.objects.count(), before)

    def test_delete_confirmation_and_post(self):
        self.assertContains(self.client.get(self.url('delete')), self.experience.title)
        self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertRedirects(self.client.post(self.url('delete')), reverse('main:show_experience'))
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_mutations_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        for url in (reverse('main:create_experience'), self.url('update'), self.url('delete')):
            self.assertEqual(client.post(url, self.payload).status_code, 403)
        response = client.get(reverse('main:create_experience'))
        token = response.cookies['csrftoken'].value
        response = client.post(reverse('main:create_experience'), {**self.payload, 'csrfmiddlewaretoken': token})
        self.assertEqual(response.status_code, 302)

    def test_unknown_ids_and_unsupported_methods(self):
        for action in ('update', 'delete'):
            url = reverse(f'main:{action}_experience', args=[uuid.uuid4()])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, self.payload).status_code, 404)
        self.assertEqual(self.client.put(self.url('update')).status_code, 405)
        self.assertEqual(self.client.delete(self.url('delete')).status_code, 405)

    def test_json_filters_and_round_trip(self):
        response = self.client.get(reverse('main:get_experience_json'), {'title': ' unique ', 'status': 'ongoing'})
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(len(response.json()), 1)
        restored = list(serializers.deserialize('json', response.content))[0].object
        self.assertEqual(restored.pk, self.experience.pk)
        self.assertEqual(restored.description, self.experience.description)
        self.assertTrue(restored.is_ongoing)
        self.assertEqual(self.client.get(reverse('main:get_experience_json'), {
            'title': 'Unique', 'status': 'completed',
        }).json(), [])
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse('main:show_experience'), {'title': 'Unique', 'status': 'completed'})
        self.assertContains(response, '1 pengalaman ditampilkan.')
        self.assertContains(response, 'Selesai')
        response = self.client.get(reverse('main:show_experience'), {'title': 'not-a-match'})
        self.assertContains(response, 'Tidak ada pengalaman yang cocok.')

    def test_page_uses_deserialized_json_and_escapes_content(self):
        self.experience.title = '<script>alert(1)</script>'
        response = HttpResponse(serializers.serialize('json', [self.experience]), content_type='application/json')
        with patch('main.views.get_experience_json', return_value=response) as endpoint:
            page = self.client.get(reverse('main:show_experience'))
        endpoint.assert_called_once()
        self.assertEqual(page.context['experience_list'][0].title, self.experience.title)
        self.assertContains(page, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(page, self.experience.title)


class ExperienceAuthorizationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'regular_user', password='SafePass123!',
        )
        self.editor = User.objects.create_user(
            'experience_editor', password='SafePass123!',
        )
        self.editor_group = Group.objects.create(name='Editor')
        self.editor.groups.add(self.editor_group)
        self.admin = User.objects.create_superuser(
            'portfolio_owner', 'portfolio@example.com', 'SafePass123!',
        )
        self.experience = Experience.objects.create(
            title='Volunteer Mentor',
            description='Mendampingi peserta belajar pemrograman.',
            category='volunteer',
        )
        self.payload = {
            'title': 'Updated Volunteer Mentor',
            'description': 'Mendampingi peserta dan menyiapkan materi.',
            'category': 'volunteer',
            'thumbnail': '',
            'ended_at': '',
        }

    def url(self, action):
        return reverse(
            f'main:{action}_experience', args=[self.experience.pk],
        )

    def test_public_can_read_but_cannot_see_crud_controls(self):
        response = self.client.get(reverse('main:show_experience'))

        self.assertContains(response, self.experience.title)
        self.assertContains(response, reverse(
            'main:toggle_experience_star', args=[self.experience.pk],
        ))
        self.assertNotContains(response, reverse('main:create_experience'))
        self.assertNotContains(response, self.url('update'))
        self.assertNotContains(response, self.url('delete'))

    def test_anonymous_user_is_redirected_to_login_for_every_action(self):
        actions = [
            ('get', reverse('main:create_experience')),
            ('get', self.url('update')),
            ('get', self.url('delete')),
            ('post', reverse(
                'main:toggle_experience_star', args=[self.experience.pk],
            )),
        ]

        for method, url in actions:
            with self.subTest(url=url):
                response = getattr(self.client, method)(url)
                self.assertRedirects(
                    response, f'{reverse("main:login")}?next={url}',
                )

    def test_regular_user_can_star_but_cannot_change_experience(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse('main:create_experience')).status_code,
            403,
        )
        self.assertEqual(self.client.get(self.url('update')).status_code, 403)
        self.assertEqual(self.client.get(self.url('delete')).status_code, 403)

        star_url = reverse(
            'main:toggle_experience_star', args=[self.experience.pk],
        )
        self.assertRedirects(
            self.client.post(star_url), reverse('main:show_experience'),
        )
        self.assertTrue(
            self.experience.starred_by.filter(pk=self.user.pk).exists(),
        )
        self.assertContains(
            self.client.get(reverse('main:show_experience')), 'Unstar',
        )
        self.client.post(star_url)
        self.assertFalse(
            self.experience.starred_by.filter(pk=self.user.pk).exists(),
        )
        self.assertEqual(self.client.get(star_url).status_code, 405)

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.client.force_login(self.editor)
        self.assertEqual(
            self.client.get(reverse('main:create_experience')).status_code,
            403,
        )
        self.assertEqual(self.client.get(self.url('delete')).status_code, 403)
        self.assertEqual(self.client.get(self.url('update')).status_code, 200)
        self.assertRedirects(
            self.client.post(self.url('update'), self.payload),
            reverse('main:show_experience'),
        )
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, self.payload['title'])

        response = self.client.get(reverse('main:show_experience'))
        self.assertContains(response, self.url('update'))
        self.assertNotContains(response, reverse('main:create_experience'))
        self.assertNotContains(response, self.url('delete'))

    def test_superuser_has_all_experience_controls(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('main:show_experience'))

        self.assertContains(response, reverse('main:create_experience'))
        self.assertContains(response, self.url('update'))
        self.assertContains(response, self.url('delete'))

    def test_experience_api_uses_username_instead_of_internal_id(self):
        self.experience.starred_by.add(self.user)
        response = self.client.get(reverse('main:get_experience_json'))
        experience_data = next(
            item for item in response.json()
            if item['pk'] == str(self.experience.pk)
        )
        starred_by = experience_data['fields']['starred_by']

        self.assertEqual(starred_by, [['regular_user']])
        self.assertNotIn(self.user.pk, starred_by)


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title='Staff of Academy Division (DSAI) - COMPFEST',
            description=(
                'Managed relations with industry mentors and lecturers, '
                'participant selection, and event operations.'
            ),
            category='volunteer',
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse('main:show_main'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertNotContains(response, self.experience.title)
        self.assertContains(
            response,
            f'href="{reverse("main:show_experience")}"',
        )

    def test_nonexistent_page_returns_404(self):
        response = self.client.get('/halaman-yang-tidak-ada/')

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(
            str(self.experience),
            'Staff of Academy Division (DSAI) - COMPFEST',
        )
        self.assertEqual(self.experience.category, 'volunteer')
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse('main:show_experience'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experience.html')
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, 'Volunteer')
        self.assertContains(response, 'Sedang berlangsung')
        self.assertContains(
            response,
            f'href="{reverse("main:show_main")}"',
        )

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse('main:show_experience'))

        self.assertContains(response, 'Belum ada pengalaman yang ditambahkan.')

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse('main:show_experience'))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, 'Selesai')


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title='SCELE Notifier',
            problem='SCELE does not send notifications automatically.',
            solution='Built a Telegram bot that scrapes SCELE and sends alerts.',
            tech_stack='Python · Telegram Bot API',
        )

    def test_projects_url_is_accessible(self):
        response = self.client.get(reverse('main:show_projects'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects.html')
        self.assertContains(
            response,
            f'href="{reverse("main:show_main")}"',
        )

    def test_project_model(self):
        self.assertEqual(str(self.project), 'SCELE Notifier')
        self.assertFalse(self.project.project_url)

    def test_projects_page_loads_ajax_shell(self):
        response = self.client.get(reverse('main:show_projects'))

        self.assertContains(response, 'id="grid"')
        self.assertContains(response, reverse('main:get_projects_json'))
        self.assertContains(response, 'fetchProjects(searchInput.value.trim())')
        self.assertContains(response, 'function escapeHtml(value)')
        self.assertNotContains(response, self.project.title)

    def test_projects_api_returns_data_and_supports_search(self):
        response = self.client.get(reverse('main:get_projects_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()[0]
        self.assertEqual(data['pk'], str(self.project.pk))
        self.assertEqual(data['fields']['title'], self.project.title)
        self.assertEqual(data['fields']['problem'], self.project.problem)
        self.assertEqual(data['fields']['solution'], self.project.solution)
        self.assertEqual(data['fields']['tech_stack'], self.project.tech_stack)
        self.assertEqual(data['fields']['star_count'], 0)
        self.assertFalse(data['fields']['is_starred'])

        filtered_data = self.client.get(reverse('main:get_projects_json'), {
            'title': 'scele',
        }).json()
        self.assertIn(str(self.project.pk), [item['pk'] for item in filtered_data])
        self.assertTrue(all(
            'scele' in item['fields']['title'].lower()
            for item in filtered_data
        ))
        self.assertEqual(
            self.client.get(reverse('main:get_projects_json'), {
                'title': 'tidak ada',
            }).json(),
            [],
        )

    def test_empty_projects_api(self):
        Project.objects.all().delete()
        response = self.client.get(reverse('main:get_projects_json'))
        self.assertEqual(response.json(), [])

    def test_project_with_url_is_in_api(self):
        self.project.project_url = 'https://github.com/williamorln/scele-notifier'
        self.project.save()
        response = self.client.get(reverse('main:get_projects_json'))

        self.assertEqual(
            response.json()[0]['fields']['project_url'],
            self.project.project_url,
        )

    def test_project_form_strips_html(self):
        form = ProjectForm(data={
            'title': '<b>Portfolio</b>',
            'problem': '<i>Data</i> tersebar',
            'solution': '<strong>Satu</strong> halaman',
            'tech_stack': '<span>Django</span>',
            'project_url': '',
        })
        self.assertTrue(form.is_valid(), form.errors)
        project = form.save()
        self.assertEqual(project.title, 'Portfolio')
        self.assertEqual(project.problem, 'Data tersebar')
        self.assertEqual(project.solution, 'Satu halaman')
        self.assertEqual(project.tech_stack, 'Django')

    def test_project_form_rejects_title_containing_only_html(self):
        form = ProjectForm(data={
            'title': '<img src=x onerror=alert(1)>',
            'problem': 'Masalah',
            'solution': 'Solusi',
            'tech_stack': 'Django',
            'project_url': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Nama proyek tidak boleh hanya berisi tag HTML.', form.errors['title'])


class AuthenticationAndAuthorizationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('visitor', password='SafePass123!')
        self.admin = User.objects.create_superuser(
            'owner', 'owner@example.com', 'SafePass123!',
        )
        self.project = Project.objects.create(
            title='Portfolio',
            problem='Project work is scattered.',
            solution='Collect it in one website.',
            tech_stack='Django',
        )

    def test_register_login_cookie_and_logout(self):
        response = self.client.post(reverse('main:register'), {
            'username': 'newuser',
            'password1': 'AnotherPass123!',
            'password2': 'AnotherPass123!',
        })
        self.assertRedirects(response, reverse('main:login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

        response = self.client.post(reverse('main:login'), {
            'username': 'newuser', 'password': 'AnotherPass123!',
        })
        self.assertRedirects(response, reverse('main:show_main'))
        self.assertIn('last_login', response.cookies)
        self.assertContains(self.client.get(reverse('main:show_main')), 'newuser')

        response = self.client.get(reverse('main:logout'))
        self.assertRedirects(response, reverse('main:show_main'))
        self.assertEqual(response.cookies['last_login']['max-age'], 0)

    def test_project_changes_are_limited_to_superuser(self):
        create_url = reverse('main:create_project')
        delete_url = reverse('main:delete_project', args=[self.project.pk])
        ajax_url = reverse('main:create_project_ajax')

        self.assertRedirects(
            self.client.get(create_url), f'{reverse("main:login")}?next={create_url}',
        )
        self.assertEqual(self.client.post(ajax_url).status_code, 403)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(create_url).status_code, 403)
        self.assertEqual(self.client.post(delete_url).status_code, 403)
        self.assertEqual(self.client.post(ajax_url).status_code, 403)
        self.assertNotContains(
            self.client.get(reverse('main:show_projects')),
            'id="add-project-modal"',
        )

        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(create_url).status_code, 200)
        response = self.client.get(reverse('main:show_projects'))
        self.assertContains(response, 'Tambah Proyek')
        self.assertContains(response, 'id="add-project-modal"')

    def test_logged_in_user_can_toggle_star(self):
        star_url = reverse('main:toggle_star', args=[self.project.pk])
        self.assertRedirects(
            self.client.post(star_url), f'{reverse("main:login")}?next={star_url}',
        )

        self.client.force_login(self.user)
        self.client.post(star_url)
        self.assertTrue(self.project.starred_by.filter(pk=self.user.pk).exists())
        project_data = self.client.get(reverse('main:get_projects_json')).json()[0]
        self.assertTrue(project_data['fields']['is_starred'])
        self.assertEqual(project_data['fields']['star_count'], 1)

        self.client.post(star_url)
        self.assertFalse(self.project.starred_by.filter(pk=self.user.pk).exists())

    def test_project_api_uses_username_instead_of_user_id(self):
        self.project.starred_by.add(self.user)
        response = self.client.get(reverse('main:get_projects_json'))
        project_data = next(
            item for item in response.json()
            if item['pk'] == str(self.project.pk)
        )
        self.assertEqual(project_data['fields']['starred_by_names'], 'visitor')
        self.assertNotIn('starred_by', project_data['fields'])

    def test_create_project_ajax(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('main:create_project_ajax'), {
            'title': 'Project AJAX',
            'problem': 'Halaman harus dimuat ulang.',
            'solution': 'Tambah data memakai Fetch API.',
            'tech_stack': 'Django, JavaScript',
            'project_url': 'https://example.com/project-ajax',
        })

        self.assertEqual(response.status_code, 201)
        self.assertIn('pk', response.json())
        self.assertTrue(Project.objects.filter(title='Project AJAX').exists())

    def test_create_project_ajax_returns_validation_errors(self):
        self.client.force_login(self.admin)
        before = Project.objects.count()
        response = self.client.post(reverse('main:create_project_ajax'), {
            'title': '<img src=x onerror=alert(1)>',
            'problem': 'Masalah',
            'solution': 'Solusi',
            'tech_stack': 'Django',
            'project_url': '',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json()['errors'])
        self.assertEqual(Project.objects.count(), before)

    def test_create_project_ajax_requires_post_and_csrf(self):
        ajax_url = reverse('main:create_project_ajax')
        self.assertEqual(self.client.get(ajax_url).status_code, 405)

        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        payload = {
            'title': 'CSRF Test',
            'problem': 'Masalah',
            'solution': 'Solusi',
            'tech_stack': 'Django',
            'project_url': '',
        }
        self.assertEqual(client.post(ajax_url, payload).status_code, 403)

        page = client.get(reverse('main:show_projects'))
        token = page.cookies['csrftoken'].value
        response = client.post(
            ajax_url,
            payload,
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)
