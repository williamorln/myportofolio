from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Experience, Project


class StarredSerializer(serializers.ModelSerializer):
    """Field star yang sama untuk model dengan relasi starred_by."""

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    def get_star_count(self, obj):
        return len(obj.starred_by.all())

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return any(user.pk == request.user.pk for user in obj.starred_by.all())

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ProjectSerializer(StarredSerializer):
    class Meta:
        model = Project
        fields = [
            "id", "title", "problem", "solution", "tech_stack", "project_url",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return value

    def validate_problem(self, value):
        return strip_tags(value).strip()

    def validate_solution(self, value):
        return strip_tags(value).strip()

    def validate_tech_stack(self, value):
        return strip_tags(value).strip()


class ExperienceSerializer(StarredSerializer):
    """Aturan validasinya sama dengan ExperienceForm di Tugas 5, hanya lewat jalur API."""

    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)

    class Meta:
        model = Experience
        fields = [
            "id", "title", "description", "category", "category_display",
            "thumbnail", "started_at", "ended_at", "is_ongoing",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id", "started_at"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Nama pengalaman tidak boleh hanya berisi tag HTML.")
        return value

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Deskripsi tidak boleh hanya berisi tag HTML.")
        return value

    def validate_thumbnail(self, value):
        value = strip_tags(value or "").strip()
        if value and not value.lower().startswith(("https://", "http://", "/static/")):
            raise serializers.ValidationError(
                "Gunakan URL HTTP(S) atau path gambar yang dimulai dengan /static/.",
            )
        return value
