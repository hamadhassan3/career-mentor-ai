from django.urls import path
from . import views

urlpatterns = [
    path('achievements/', views.ProgressAchievementListView.as_view(), name='progress-achievements-list'),
    path('achievements/create/', views.create_progress_achievement, name='progress-achievements-create'),
    path('achievements/<int:achievement_id>/delete/', views.delete_progress_achievement, name='progress-achievements-delete'),
]