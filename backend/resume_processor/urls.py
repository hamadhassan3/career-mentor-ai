from django.urls import path
from . import views

urlpatterns = [
    path('resumes/upload', views.upload_resume, name='upload_resume'),
    path('skills/all', views.get_all_skills, name='get_all_skills'),
    path('skills/it', views.get_it_skills, name='get_it_skills'),
    path('skills/soft', views.get_soft_skills, name='get_soft_skills'),
    path('skills/languages', views.get_languages, name='get_languages'),
    path('designations', views.get_designations, name='get_designations'),
    path('predict', views.predict_skills, name='predict_skills'),
    path('predict_next_skill', views.predict_single_skill, name='predict_single_skill'),
]