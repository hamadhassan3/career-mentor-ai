from django.urls import path
from .views import (
    ResumeUploadView,
    ITSkillsView,
    SoftSkillsView,
    LanguageSkillsView,
    AllSkillsView
)

urlpatterns = [
    path('upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('skills/it/', ITSkillsView.as_view(), name='it-skills'),
    path('skills/soft/', SoftSkillsView.as_view(), name='soft-skills'),
    path('skills/languages/', LanguageSkillsView.as_view(), name='language-skills'),
    path('skills/all/', AllSkillsView.as_view(), name='all-skills'),
]