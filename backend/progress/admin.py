from django.contrib import admin
from .models import ProgressAchievement


@admin.register(ProgressAchievement)
class ProgressAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'created_at']
    list_filter = ['skill', 'created_at']
    search_fields = ['user__username', 'user__email', 'skill']
    readonly_fields = ['created_at']
    ordering = ['-created_at']