import uuid

from django.contrib.auth.models import User
from django.db import models


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='full-time',
    )
    thumbnail = models.CharField(max_length=500, blank=True, null=True)
    starred_by = models.ManyToManyField(
        User, related_name='starred_experiences', blank=True,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    problem = models.TextField()
    solution = models.TextField()
    tech_stack = models.CharField(max_length=255)
    project_url = models.URLField(blank=True, null=True)
    starred_by = models.ManyToManyField(
        User, related_name='starred_projects', blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
