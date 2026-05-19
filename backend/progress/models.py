from django.db import models
from django.contrib.auth.models import User


class ProgressAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_achievements')
    skill = models.CharField(max_length=255)
    image_url = models.URLField(max_length=500)
    s3_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.skill}"