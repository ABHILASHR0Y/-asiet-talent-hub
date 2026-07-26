from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.TextField(blank=True, default='')
    experience = models.TextField(blank=True, default='')
    projects = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def get_skills_list(self):
        """Return a list of skills, properly split and cleaned"""
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]

class RecruiterSearch(models.Model):
    search_query = models.TextField()
    filters_used = models.JSONField(default=dict)
    searched_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.search_query[:50]}..."

class Analytics(models.Model):
    skill_name = models.CharField(max_length=255)
    search_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Analytics"

    def __str__(self):
        return f"{self.skill_name} ({self.search_count} searches)"

class SkillFilter(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the skill (e.g., Python, JavaScript)")
    display_name = models.CharField(max_length=100, help_text="How the skill should be displayed (e.g., Python, JavaScript)")
    is_active = models.BooleanField(default=True, help_text="Whether this skill filter is active and should be shown")
    order = models.PositiveIntegerField(default=0, help_text="Order in which the skill appears (lower numbers appear first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Skill Filter"
        verbose_name_plural = "Skill Filters"

    def __str__(self):
        return self.display_name
