import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Project


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
