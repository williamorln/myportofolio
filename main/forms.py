from django.forms import ModelForm, TextInput, Textarea, URLInput

from main.models import Project


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
