from django.db import models
from django.contrib.postgres.fields import ArrayField


class Resume(models.Model):
    total_exp = models.IntegerField(default=0)
    
    university = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    designition = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    degree = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    skills = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    companies_worked_at = ArrayField(
        models.TextField(),
        blank=True,
        default=list
    )
    
    skills_original = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    it_skills = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    it_skill_categories = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    soft_skills = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    soft_skill_categories = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    languages = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    language_categories = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resumes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Resume - {self.id}"
