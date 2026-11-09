import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        # migrasi seed sudah mengisi beberapa proyek, kosongkan agar hitungan test pasti
        Project.objects.all().delete()
        self.project = Project.objects.create(
            title="Portfolio", problem="Butuh etalase karya.",
            solution="Website portofolio dengan Django.", tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "problem": "Jadwal belajar berantakan.",
            "solution": "Aplikasi penjadwal.", "tech_stack": "Python",
            "project_url": "https://example.com/",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_response_only_exposes_declared_fields(self):
        self.project.starred_by.add(self.visitor)
        item = self.client.get(self.detail_url).data
        self.assertEqual(set(item), {
            "id", "title", "problem", "solution", "tech_stack", "project_url",
            "star_count", "is_starred", "starred_by_names",
        })
        self.assertEqual(item["starred_by_names"], "visitor")
        self.assertNotIn("password", str(item))
        self.assertNotIn("email", str(item))

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_permission_is_checked_before_object_lookup(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.patch(url, {"title": "x"}, format="json").status_code, 403)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.patch(url, {"title": "x"}, format="json").status_code, 404)

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_create_ignores_client_supplied_id(self):
        self.client.force_authenticate(user=self.owner)
        chosen = str(uuid.uuid4())
        response = self.client.post(self.list_url, {**self.payload, "id": chosen}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["id"], chosen)

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
            ({"problem": None}, "problem"),
        ]:
            with self.subTest(changes=changes):
                response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_html_is_stripped_from_text_fields(self):
        self.client.force_authenticate(user=self.owner)
        payload = {**self.payload, "title": "<b>Bold</b> title", "tech_stack": "<i>Django</i>"}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.data["title"], "Bold title")
        self.assertEqual(response.data["tech_stack"], "Django")

    def test_optional_url_can_be_omitted_or_blank(self):
        self.client.force_authenticate(user=self.owner)
        without_url = {key: value for key, value in self.payload.items() if key != "project_url"}
        self.assertEqual(self.client.post(self.list_url, without_url, format="json").status_code, 201)
        blank_url = {**self.payload, "project_url": ""}
        self.assertEqual(self.client.post(self.list_url, blank_url, format="json").status_code, 201)

    def test_malformed_json_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, "{not json", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_changes_only_sent_fields(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Updated"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Updated")
        self.assertEqual(self.project.problem, "Butuh etalase karya.")

    def test_put_requires_all_required_fields(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.detail_url, {"title": "Only title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("problem", response.data)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "New project")

    def test_invalid_patch_does_not_write(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "<b></b>"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_404_NOT_FOUND)

    def test_unsupported_methods(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.put(self.list_url, self.payload, format="json").status_code, 405)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)
        self.assertEqual(self.client.post(self.detail_url, self.payload, format="json").status_code, 405)

    def test_star_toggles_for_logged_in_user(self):
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(response.data["starred_by_names"], "visitor")
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_star_state_is_per_viewer(self):
        self.project.starred_by.add(self.visitor)
        self.client.force_authenticate(user=self.visitor)
        self.assertTrue(self.client.get(self.detail_url).data["is_starred"])
        self.client.force_authenticate(user=self.owner)
        item = self.client.get(self.detail_url).data
        self.assertFalse(item["is_starred"])
        self.assertEqual(item["star_count"], 1)

    def test_star_requires_login_and_post(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.assertEqual(self.client.get(self.star_url).status_code, 403)
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_star_missing_project(self):
        self.client.force_authenticate(user=self.visitor)
        url = reverse("api:project-star", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_session_writes_require_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

        # token CSRF dibuat saat halaman Projects dibuka oleh pengguna yang login
        token = client.get(reverse("main:show_projects")).cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_staff_and_editor_cannot_manage_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_session_write_with_token_from_browsable_api(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # form Browsable API ikut merender token CSRF yang asli
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_legacy_endpoints_still_available(self):
        self.assertEqual(self.client.get(reverse("main:get_projects_json")).status_code, 200)
        self.assertEqual(self.client.get(reverse("main:show_projects")).status_code, 200)


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.editor = User.objects.create_user(username="editor", password="test-password")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        # migrasi seed sudah mengisi data experience, kosongkan agar hitungan test pasti
        Experience.objects.all().delete()
        self.experience = Experience.objects.create(
            title="Volunteer Mentor", description="Mendampingi peserta belajar.",
            category="volunteer",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "Research Assistant", "description": "Analisis data penelitian.",
            "category": "research", "thumbnail": "/static/img/research.jpg",
            "ended_at": None,
        }

    def test_public_list_and_detail_shape(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data[0]
        self.assertEqual(item["id"], str(self.experience.id))
        self.assertEqual(item["category_display"], "Volunteer")
        self.assertTrue(item["is_ongoing"])
        self.assertIsNone(item["ended_at"])
        self.assertFalse(item["is_starred"])
        self.assertNotIn("fields", item)
        self.assertEqual(set(item), {
            "id", "title", "description", "category", "category_display",
            "thumbnail", "started_at", "ended_at", "is_ongoing",
            "star_count", "is_starred", "starred_by_names",
        })
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_filters_and_empty_results(self):
        Experience.objects.create(
            title="Finished Internship", description="Selesai.", category="internship",
            ended_at=timezone.now(),
        )
        self.assertEqual(len(self.client.get(self.list_url, {"title": " MENTOR "}).data), 1)
        ongoing = self.client.get(self.list_url, {"status": "ongoing"}).data
        self.assertEqual([item["title"] for item in ongoing], ["Volunteer Mentor"])
        completed = self.client.get(self.list_url, {"status": "completed"}).data
        self.assertEqual([item["title"] for item in completed], ["Finished Internship"])
        self.assertFalse(completed[0]["is_ongoing"])
        self.assertEqual(len(self.client.get(self.list_url, {"status": "bogus"}).data), 2)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_list_is_ordered_by_category_then_title(self):
        Experience.objects.create(title="A Internship", description="x", category="internship")
        categories = [item["category"] for item in self.client.get(self.list_url).data]
        self.assertEqual(categories, sorted(categories))

    def test_missing_experience(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_regular_user_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Volunteer Mentor")

    def test_editor_can_update_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        # penolakan harus benar-benar tidak menyentuh database
        self.assertEqual(Experience.objects.count(), 1)
        self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertFalse(Experience.objects.filter(title=self.payload["title"]).exists())
        response = self.client.patch(self.detail_url, {"title": "Edited by editor"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Edited by editor")
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Experience.objects.count(), 1)

    def test_editor_role_is_group_based_not_staff_based(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permission_is_checked_before_object_lookup(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.patch(url, {"title": "x"}, format="json").status_code, 403)
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.patch(url, {"title": "x"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(url).status_code, 403)

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Experience.objects.get(pk=response.data["id"])
        self.assertIsNotNone(created.started_at)
        self.assertTrue(response.data["is_ongoing"])

        url = reverse("api:experience-detail", args=[created.pk])
        response = self.client.patch(url, {"ended_at": "2026-09-20T12:30"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_ongoing"])
        self.assertEqual(response.data["description"], "Analisis data penelitian.")

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_put_requires_all_required_fields(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.detail_url, {"title": "Only title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"description": "<script></script>"}, "description"),
            ({"category": "unknown"}, "category"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
            ({"ended_at": "not a date"}, "ended_at"),
        ]:
            with self.subTest(changes=changes):
                response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
        self.assertEqual(Experience.objects.count(), 1)

    def test_html_is_stripped_and_blank_thumbnail_allowed(self):
        self.client.force_authenticate(user=self.owner)
        payload = {
            **self.payload, "title": "<b>Research</b> Assistant",
            "description": "<em>Analisis</em> data.", "thumbnail": "",
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Research Assistant")
        self.assertEqual(response.data["description"], "Analisis data.")
        without_thumbnail = {k: v for k, v in self.payload.items() if k != "thumbnail"}
        self.assertEqual(self.client.post(self.list_url, without_thumbnail, format="json").status_code, 201)

    def test_server_managed_fields_cannot_be_forged(self):
        self.client.force_authenticate(user=self.owner)
        chosen = str(uuid.uuid4())
        response = self.client.post(self.list_url, {
            **self.payload, "id": chosen, "started_at": "2000-01-01T00:00:00Z",
            "is_ongoing": False, "star_count": 99, "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["id"], chosen)
        self.assertTrue(response.data["started_at"].startswith(str(timezone.now().year)))
        self.assertTrue(response.data["is_ongoing"])
        self.assertEqual(response.data["star_count"], 0)

    def test_star_toggles_for_any_logged_in_user(self):
        for user in (self.visitor, self.editor):
            self.client.force_authenticate(user=user)
            response = self.client.post(self.star_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 2)
        self.assertEqual(response.data["starred_by_names"], "editor, visitor")
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

    def test_star_requires_login_post_and_existing_object(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.assertEqual(self.client.get(self.star_url).status_code, 403)
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)
        url = reverse("api:experience-star", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_star_state_is_per_viewer(self):
        self.experience.starred_by.add(self.visitor)
        self.client.force_authenticate(user=self.visitor)
        self.assertTrue(self.client.get(self.detail_url).data["is_starred"])
        self.client.force_authenticate(user=self.editor)
        item = self.client.get(self.detail_url).data
        self.assertFalse(item["is_starred"])
        self.assertEqual(item["star_count"], 1)

    def test_session_writes_require_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="editor", password="test-password")
        response = client.patch(self.detail_url, {"title": "No token"}, format="json")
        self.assertEqual(response.status_code, 403)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Volunteer Mentor")

        # halaman Experience merender token CSRF, jadi cookie-nya dibuat di sini
        token = client.get(reverse("main:show_experience")).cookies["csrftoken"].value
        response = client.patch(
            self.detail_url, {"title": "With token"}, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsupported_methods(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.put(self.list_url, self.payload, format="json").status_code, 405)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)
        self.assertEqual(self.client.post(self.detail_url, self.payload, format="json").status_code, 405)

    def test_browsable_api_opens(self):
        for url in (self.list_url, self.detail_url):
            response = self.client.get(url, HTTP_ACCEPT="text/html")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("text/html", response["Content-Type"])

    def test_legacy_views_follow_the_same_roles(self):
        # view lama dari Tugas 3-5 tidak boleh memberi hak lebih luas daripada API
        legacy_payload = {
            "title": "Legacy", "description": "x", "category": "research",
            "thumbnail": "", "ended_at": "",
        }
        delete_url = reverse("main:delete_experience", args=[self.experience.pk])
        edit_url = reverse("main:update_experience", args=[self.experience.pk])
        self.client.force_login(self.editor)
        self.assertEqual(self.client.post(reverse("main:create_experience"), legacy_payload).status_code, 403)
        self.assertEqual(self.client.post(reverse("main:create_experience_ajax"), legacy_payload).status_code, 403)
        self.assertEqual(self.client.post(delete_url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.assertEqual(self.client.get(edit_url).status_code, 200)
        self.client.force_login(self.visitor)
        self.assertEqual(self.client.get(edit_url).status_code, 403)

    def test_experience_page_uses_api_endpoints(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, f'data-list-endpoint="{self.list_url}"')
        self.assertContains(response, "data-detail-url-template")
        self.assertNotContains(response, reverse("main:get_experience_json"))
        self.assertContains(response, "/static/js/ajax-utils.js")

    def test_legacy_endpoints_still_available(self):
        self.assertEqual(self.client.get(reverse("main:get_experience_json")).status_code, 200)
        self.assertEqual(self.client.get(reverse("main:show_experience")).status_code, 200)
