
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ResumeListCreateView.as_view(), name='resume-list-create'),
    path('<int:pk>/', views.ResumeDetailView.as_view(), name='resume-detail'),
    path('upload/', views.create_resume_from_upload, name='resume-upload'),
    path('latest/', views.get_latest_resume, name='resume-latest'),
]