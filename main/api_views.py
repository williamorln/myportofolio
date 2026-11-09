from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Experience, Project
from main.permissions import (
    IsPortfolioOwnerOrEditorOrReadOnly, IsPortfolioOwnerOrReadOnly,
)
from main.serializers import ExperienceSerializer, ProjectSerializer


def _detail_response(request, queryset, serializer_class, object_id):
    """GET/PUT/PATCH/DELETE satu objek; dipakai bersama oleh Project dan Experience."""
    instance = get_object_or_404(queryset, pk=object_id)
    if request.method in ("GET", "HEAD"):
        serializer = serializer_class(instance, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = serializer_class(
        instance, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


def _toggle_star(request, model, serializer_class, object_id):
    instance = get_object_or_404(model, pk=object_id)
    if instance.starred_by.filter(pk=request.user.pk).exists():
        instance.starred_by.remove(request.user)
    else:
        instance.starred_by.add(request.user)
    serializer = serializer_class(instance, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    if request.method in ("GET", "HEAD"):
        # urutan sama seperti endpoint lama: proyek terbaru di atas
        projects = Project.objects.prefetch_related("starred_by").order_by(
            "-created_at", "title", "id",
        )
        title = request.query_params.get("title", "").strip()
        if title:
            projects = projects.filter(title__icontains=title)
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    return _detail_response(
        request, Project.objects.prefetch_related("starred_by"),
        ProjectSerializer, project_id,
    )


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    return _toggle_star(request, Project, ProjectSerializer, project_id)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    if request.method in ("GET", "HEAD"):
        experiences = Experience.objects.prefetch_related("starred_by").order_by(
            "category", "title", "id",
        )
        title = request.query_params.get("title", "").strip()
        progress = request.query_params.get("status", "")
        if title:
            experiences = experiences.filter(title__icontains=title)
        # nilai status selain ongoing/completed diabaikan, sama seperti endpoint lama
        if progress in ("ongoing", "completed"):
            experiences = experiences.filter(ended_at__isnull=progress == "ongoing")
        serializer = ExperienceSerializer(
            experiences, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ExperienceSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    return _detail_response(
        request, Experience.objects.prefetch_related("starred_by"),
        ExperienceSerializer, experience_id,
    )


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_star(request, experience_id):
    return _toggle_star(request, Experience, ExperienceSerializer, experience_id)
