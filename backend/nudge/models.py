import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Nudge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nudges')
    content = models.TextField()
    langfuse_trace_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Nudge for {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
    
    @property
    def is_stale(self):
        """Check if nudge is older than 24 hours"""
        return timezone.now() - self.created_at > timezone.timedelta(days=1)
    
    @classmethod
    def get_latest_for_user(cls, user):
        """Get the latest nudge for a user"""
        return cls.objects.filter(user=user).first()
