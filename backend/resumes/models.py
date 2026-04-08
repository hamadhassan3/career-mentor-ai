from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255, blank=True, null=True)
    target_designation = models.CharField(max_length=255, blank=True, null=True)
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    total_exp = models.IntegerField(default=0)
    
    university = models.JSONField(default=list, blank=True)
    designition = models.JSONField(default=list, blank=True)
    degree = models.JSONField(default=list, blank=True)
    skills = models.JSONField(default=list, blank=True)
    companies_worked_at = models.JSONField(default=list, blank=True)
    skills_original = models.JSONField(default=list, blank=True)
    it_skills = models.JSONField(default=list, blank=True)
    it_skill_categories = models.JSONField(default=list, blank=True)
    soft_skills = models.JSONField(default=list, blank=True)
    soft_skill_categories = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)
    language_categories = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resumes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title or self.original_filename or f'Resume {self.id}'}"
