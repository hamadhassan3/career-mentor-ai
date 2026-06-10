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
    
    is_active = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resumes'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_active'],
                condition=models.Q(is_active=True),
                name='one_active_resume_per_user'
            )
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title or self.original_filename or f'Resume {self.id}'}"


class NextBestStep(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='next_step')
    title = models.CharField(max_length=255)
    skill_type = models.CharField(max_length=50, blank=True, null=True)  # IT/Soft skill
    confidence = models.FloatField(blank=True, null=True)
    impact = models.CharField(max_length=20, blank=True, null=True)  # High/Medium/Low
    recommended_skills = models.JSONField(default=list, blank=True)
    target_designation = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'next_best_steps'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.resume.user.username} - Next Step: {self.title}"


class SkillCourseRecommendation(models.Model):
    """
    Cached course/YouTube recommendations for a resume's next best skill.

    Generated once from the external recommendation service and persisted so
    page refreshes read from the database instead of re-calling the service.
    Tied to NextBestStep via CASCADE so it is removed automatically when the
    next best skill is deleted or regenerated.
    """
    next_step = models.OneToOneField(NextBestStep, on_delete=models.CASCADE, related_name='course_recommendation')
    skill = models.CharField(max_length=255)  # The skill the recommendations were generated for
    courses = models.JSONField(default=list, blank=True)  # Common response structure (courses + youtube)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'skill_course_recommendations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.next_step.resume.user.username} - Courses: {self.skill}"


class CareerPathway(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='career_path')
    current_level = models.CharField(max_length=255, blank=True, null=True)
    target_role = models.CharField(max_length=255, blank=True, null=True)
    timeline_total = models.CharField(max_length=50, blank=True, null=True)  # "2-3 years"
    target_designation = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'career_pathways'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.resume.user.username} - Career Path: {self.current_level} → {self.target_role}"


class CareerStage(models.Model):
    STATUS_CHOICES = [
        ('current', 'Current'),
        ('upcoming', 'Upcoming'),
        ('future', 'Future'),
    ]
    
    pathway = models.ForeignKey(CareerPathway, on_delete=models.CASCADE, related_name='stages')
    title = models.CharField(max_length=255)
    duration = models.CharField(max_length=50)  # "3-6 months"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    skills = models.JSONField(default=list, blank=True)
    milestones = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'career_stages'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.pathway.resume.user.username} - Stage: {self.title}"
