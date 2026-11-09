from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_editor(user):
    """Editor = anggota grup "Editor" (peran dari Tugas 4), bukan sekadar is_staff."""
    return (
        user.is_authenticated
        and user.groups.filter(name="Editor").exists()
    )


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """Semua orang boleh membaca, hanya pemilik (superuser) yang boleh menulis."""

    message = "Hanya pemilik portofolio yang dapat mengubah proyek."

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
        )


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """
    Empat peran Tugas 4 pada satu kelas:
    - baca (GET/HEAD/OPTIONS): semua pengunjung
    - PUT/PATCH: pemilik dan Editor
    - POST/DELETE: hanya pemilik

    Star tidak lewat sini, endpoint itu cukup memakai IsAuthenticated.
    """

    message = (
        "Hanya pemilik portofolio yang dapat menambah atau menghapus pengalaman, "
        "sedangkan Editor hanya dapat mengubahnya."
    )

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or request.user.is_superuser:
            return True
        return request.method in ("PUT", "PATCH") and is_editor(request.user)
