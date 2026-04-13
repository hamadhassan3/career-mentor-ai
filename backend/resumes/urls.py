
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ResumeListCreateView.as_view(), name='resume-list-create'),
    path('<int:pk>/', views.ResumeDetailView.as_view(), name='resume-detail'),
    path('<int:pk>/activate/', views.activate_resume, name='resume-activate'),
    path('upload/', views.create_resume_from_upload, name='resume-upload'),
    path('latest/', views.get_latest_resume, name='resume-latest'),
    path('active/', views.get_active_resume, name='resume-active'),
]