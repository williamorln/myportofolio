from django.core.exceptions import ValidationError
from django.forms import DateTimeInput, ModelForm, TextInput, Textarea, URLInput
from django.utils.html import strip_tags

from main.models import Experience, Project


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        # started_at is an automatic creation timestamp; ended_at is user data.
        fields = ['title', 'description', 'category', 'thumbnail', 'ended_at']
        labels = {
            'title': 'Nama pengalaman',
            'description': 'Deskripsi',
            'category': 'Kategori',
            'thumbnail': 'Alamat gambar',
            'ended_at': 'Waktu selesai (UTC)',
        }
        help_texts = {
            'thumbnail': 'Opsional. Gunakan URL HTTPS atau path /static/ untuk gambar lokal.',
            'ended_at': 'Kosongkan jika masih berlangsung. Waktu menggunakan UTC.',
        }
        widgets = {
            'description': Textarea(attrs={'rows': 5}),
            'thumbnail': TextInput(attrs={'placeholder': '/static/img/foto.jpg'}),
            'ended_at': DateTimeInput(
                format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'},
            ),
        }


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "problem",
            "solution",
            "tech_stack",
            "project_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "problem": "Masalah yang Diselesaikan",
            "solution": "Solusi yang Dibangun",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "problem": Textarea(
                attrs={
                    "placeholder": "Masalah apa yang coba diselesaikan proyek ini?",
                    "rows": 3,
                }
            ),
            "solution": Textarea(
                attrs={
                    "placeholder": "Bagaimana proyek ini menyelesaikannya?",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/username/repo",
                }
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_problem(self):
        return strip_tags(self.cleaned_data["problem"]).strip()

    def clean_solution(self):
        return strip_tags(self.cleaned_data["solution"]).strip()

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()
